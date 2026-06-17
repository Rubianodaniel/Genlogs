# Genlogs Technical Test — parsed requirements

> Verbatim parse of the assessment PDF, structured for the harness.

## Context

Genlogs collects high-definition images from highway cameras across the US and
processes them to track commercial trucks nationwide. On capture, the system
detects license-plate characters, truck IDs and company logos. Once a USDOT
number is identified, it integrates with the SAFER FMCSA API to associate the
detection with carrier/vehicle records. A web portal lets users enter an origin
and destination city to see which carriers move the highest volume of trucks
between them.

## Assignment

1. **Read the whole test first.** Before solving, email the hiring manager:
   - (a) the implementation plan,
   - (b) the time you estimate to implement the plan,
   - (c) delivery date/hour,
   - (d) **wait for green light** from the hiring manager before proceeding.
2. **Architecture/design** of the Genlogs platform: which modules/components,
   and how information flows between them.
3. **Database design**: tables and schema for the platform.
4. **Spec-Driven Development (SDD)** — build a small app that simulates the
   portal. No database required. Specs:
   - (a) **Frontend (React JS):** single page that captures fields and sends them
     to the backend:
     1. From (city) — Google Maps match
     2. To (city) — Google Maps match
     3. "Search" button
     4. On Search: show a map with the 3 fastest routes between the 2 cities
        (embedded Google Maps)
     5. Render a list of carriers returned by the backend
   - (b) **Backend (FastAPI):** endpoint receiving (from_city, to_city):
     1. New York City → Washington DC:
        - Knight-Swift Transport Services (10 trucks/day)
        - J.B. Hunt Transport Services Inc (7 trucks/day)
        - YRC Worldwide (5 trucks/day)
     2. San Francisco → Los Angeles:
        - XPO Logistics (9 trucks/day)
        - Schneider (6 trucks/day)
        - Landstar Systems (2 trucks/day)
     3. Any other origin/destination (not NYC/SF → not Washington DC / LA):
        - UPS Inc. (11 trucks/day)
        - FedEx Corp (9 trucks/day)
   - (c) Share the code URL on a versioning server (GitHub, GitLab, Bitbucket).
   - (d) Push the prompts and the rules used to the repository.
   - (e) Deploy the project to a cloud provider (AWS, GCP, other) and share the URL.
5. **Report time spent** to the interviewer; if it differs from the point-1
   estimate, explain why.

> Questions about the test can be emailed to the interviewer.
