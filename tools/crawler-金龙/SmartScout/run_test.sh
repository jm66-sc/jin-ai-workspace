#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python src/run_full_pipeline.py --url "https://search.ccgp.gov.cn/bxsearch?searchtype=2&page_index=1&start_time=&end_time=&timeType=2&searchparam=&searchchannel=0&dbselect=bidx&kw=机电%E3%80%82+&bidSort=0&pinMu=0&bidType=0&buyerName=&projectId=&displayZone=&zoneId=&agentName" 2>&1 | tee logs/full_pipeline_$(date +%Y%m%d_%H%M%S).log