const { app, BrowserWindow, ipcMain, Menu } = require('electron');
const path = require('path');
const { spawn, exec } = require('child_process');
const fs = require('fs');

// 全局变量
let mainWindow = null;
let pythonProcess = null;
const isDevelopment = process.env.NODE_ENV === 'development';

// Python后端配置
const pythonBackendPath = path.join(__dirname, '..', 'dist-python', 'main');
const pythonExecutable = process.platform === 'win32' ? 'main.exe' : 'main';

// 应用数据目录
const userDataPath = app.getPath('userData');
const appDataPath = path.join(userDataPath, 'SmartScout');

class Application {
  constructor() {
    this.setupDirectories();
    this.setupAppListeners();
  }

  setupDirectories() {
    // 创建应用数据目录
    const dirs = [
      appDataPath,
      path.join(appDataPath, 'logs'),
      path.join(appDataPath, 'data'),
      path.join(appDataPath, 'config')
    ];

    dirs.forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    });

    // 复制配置文件到应用数据目录（如果不存在）
    const configFiles = ['settings.yaml', 'secrets.yaml'];
    configFiles.forEach(configFile => {
      const sourcePath = path.join(__dirname, '..', 'config', configFile);
      const destPath = path.join(appDataPath, 'config', configFile);

      if (fs.existsSync(sourcePath) && !fs.existsSync(destPath)) {
        fs.copyFileSync(sourcePath, destPath);
      }
    });

    // 复制数据库文件（如果不存在）
    const dbSource = path.join(__dirname, '..', 'data', 'database.sqlite');
    const dbDest = path.join(appDataPath, 'data', 'database.sqlite');
    if (fs.existsSync(dbSource) && !fs.existsSync(dbDest)) {
      fs.copyFileSync(dbSource, dbDest);
    }
  }

  setupAppListeners() {
    app.whenReady().then(() => {
      this.createWindow();
      this.setupMenu();
      this.startBackend();
    });

    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        this.stopBackend(() => {
          app.quit();
        });
      }
    });

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        this.createWindow();
      }
    });

    app.on('before-quit', (event) => {
      event.preventDefault(); // 阻止立即退出
      this.stopBackend(() => {
        app.exit(0);
      });
    });
  }

  createWindow() {
    mainWindow = new BrowserWindow({
      width: 1400,
      height: 900,
      minWidth: 1200,
      minHeight: 800,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, 'preload.js')
      },
      icon: path.join(__dirname, 'assets', 'icon.png'),
      show: false
    });

    // 加载前端页面
    if (isDevelopment) {
      // 开发模式：加载Vite开发服务器
      mainWindow.loadURL('http://localhost:3001');
      mainWindow.webContents.openDevTools();
    } else {
      // 生产模式：加载构建后的文件
      const frontendPath = path.join(__dirname, '..', 'frontend', 'dist', 'index.html');
      mainWindow.loadFile(frontendPath);
    }

    mainWindow.once('ready-to-show', () => {
      mainWindow.show();
      mainWindow.webContents.send('backend-status', 'starting');
    });

    mainWindow.webContents.on('did-finish-load', () => {
      // 发送应用信息到前端
      mainWindow.webContents.send('app-info', {
        version: app.getVersion(),
        platform: process.platform,
        dataPath: appDataPath,
        isPackaged: app.isPackaged
      });
    });

    // 处理前端消息
    ipcMain.handle('get-backend-status', () => {
      return pythonProcess ? 'running' : 'stopped';
    });

    ipcMain.handle('restart-backend', () => {
      this.restartBackend();
    });

    ipcMain.handle('get-logs', () => {
      const logPath = path.join(appDataPath, 'logs', 'backend.log');
      if (fs.existsSync(logPath)) {
        try {
          return fs.readFileSync(logPath, 'utf8');
        } catch (error) {
          return `读取日志失败: ${error.message}`;
        }
      }
      return '暂无日志';
    });
  }

  setupMenu() {
    const template = [
      {
        label: '文件',
        submenu: [
          {
            label: '打开数据目录',
            click: () => {
              const { shell } = require('electron');
              shell.openPath(appDataPath);
            }
          },
          {
            label: '打开日志目录',
            click: () => {
              const { shell } = require('electron');
              shell.openPath(path.join(appDataPath, 'logs'));
            }
          },
          { type: 'separator' },
          { label: '退出', role: 'quit' }
        ]
      },
      {
        label: '视图',
        submenu: [
          { label: '重新加载', role: 'reload' },
          { label: '强制重新加载', role: 'forceReload' },
          { type: 'separator' },
          { label: '开发者工具', role: 'toggleDevTools' },
          { type: 'separator' },
          { label: '重置缩放', role: 'resetZoom' },
          { label: '放大', role: 'zoomIn' },
          { label: '缩小', role: 'zoomOut' }
        ]
      },
      {
        label: '帮助',
        submenu: [
          {
            label: '关于 SmartScout',
            click: () => {
              const { dialog } = require('electron');
              dialog.showMessageBox({
                type: 'info',
                title: '关于 SmartScout',
                message: 'SmartScout 智能网页采集与规则沉淀系统',
                detail: `版本: ${app.getVersion()}\n数据目录: ${appDataPath}\nPython后端: ${pythonProcess ? '运行中' : '已停止'}`
              });
            }
          }
        ]
      }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
  }

  startBackend() {
    if (pythonProcess) {
      console.log('后端已在运行中');
      return;
    }

    // 设置环境变量
    const env = {
      ...process.env,
      SMARTSCOUT_DATA_PATH: appDataPath,
      SMARTSCOUT_CONFIG_PATH: path.join(appDataPath, 'config')
    };

    // 检查Python可执行文件是否存在
    const pythonPath = path.join(pythonBackendPath, pythonExecutable);
    if (!fs.existsSync(pythonPath)) {
      console.error(`Python可执行文件不存在: ${pythonPath}`);
      if (mainWindow) {
        mainWindow.webContents.send('backend-status', 'error');
        mainWindow.webContents.send('backend-error', `Python可执行文件不存在: ${pythonPath}`);
      }
      return;
    }

    console.log(`启动Python后端: ${pythonPath}`);

    // 启动Python进程
    pythonProcess = spawn(pythonPath, ['--port', '8000'], {
      env: env,
      cwd: path.dirname(pythonPath),
      stdio: ['pipe', 'pipe', 'pipe']
    });

    // 处理标准输出
    pythonProcess.stdout.on('data', (data) => {
      const output = data.toString().trim();
      console.log(`Python后端: ${output}`);

      // 写入日志文件
      const logPath = path.join(appDataPath, 'logs', 'backend.log');
      fs.appendFileSync(logPath, `[${new Date().toISOString()}] ${output}\n`);

      // 发送到前端
      if (mainWindow) {
        mainWindow.webContents.send('backend-output', output);

        // 检测后端启动成功
        if (output.includes('Uvicorn running') || output.includes('Application startup complete')) {
          mainWindow.webContents.send('backend-status', 'running');
        }
      }
    });

    // 处理错误输出
    pythonProcess.stderr.on('data', (data) => {
      const error = data.toString().trim();
      console.error(`Python后端错误: ${error}`);

      const logPath = path.join(appDataPath, 'logs', 'backend.log');
      fs.appendFileSync(logPath, `[${new Date().toISOString()}] ERROR: ${error}\n`);

      if (mainWindow) {
        mainWindow.webContents.send('backend-error', error);
      }
    });

    // 处理进程退出
    pythonProcess.on('close', (code) => {
      console.log(`Python后端进程退出，代码: ${code}`);
      pythonProcess = null;

      if (mainWindow) {
        mainWindow.webContents.send('backend-status', 'stopped');
      }
    });

    pythonProcess.on('error', (error) => {
      console.error(`启动Python后端失败: ${error.message}`);
      pythonProcess = null;

      if (mainWindow) {
        mainWindow.webContents.send('backend-status', 'error');
        mainWindow.webContents.send('backend-error', error.message);
      }
    });
  }

  stopBackend(callback) {
    if (!pythonProcess) {
      if (callback) callback();
      return;
    }

    console.log('正在停止Python后端...');

    // 发送停止信号
    if (mainWindow) {
      mainWindow.webContents.send('backend-status', 'stopping');
    }

    // 尝试优雅停止
    pythonProcess.on('close', () => {
      console.log('Python后端已停止');
      pythonProcess = null;
      if (callback) callback();
    });

    // 杀死进程
    pythonProcess.kill('SIGTERM');

    // 如果5秒后仍未停止，强制终止
    setTimeout(() => {
      if (pythonProcess) {
        console.log('强制终止Python后端');
        pythonProcess.kill('SIGKILL');
        pythonProcess = null;
      }
      if (callback) callback();
    }, 5000);
  }

  restartBackend() {
    console.log('重启Python后端...');
    if (mainWindow) {
      mainWindow.webContents.send('backend-status', 'restarting');
    }

    this.stopBackend(() => {
      setTimeout(() => {
        this.startBackend();
      }, 1000);
    });
  }
}

// 启动应用
new Application();