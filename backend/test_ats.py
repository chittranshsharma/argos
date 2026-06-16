import sys
import os
import logging
sys.path.append(os.getcwd())

from app.agents.jobs_agent import JobsAgent

logging.basicConfig(level=logging.INFO)

agent = JobsAgent()

print("Testing Ashby:")
ashby_jobs = agent._extract_ashby("https://jobs.ashbyhq.com/notion")
print(f"Ashby found {len(ashby_jobs)} jobs. Example:", ashby_jobs[0] if ashby_jobs else "None")

print("\nTesting Workday:")
workday_jobs = agent._extract_workday("https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite")
print(f"Workday found {len(workday_jobs)} jobs. Example:", workday_jobs[0] if workday_jobs else "None")

