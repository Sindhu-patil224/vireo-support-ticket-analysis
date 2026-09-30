Vireo Audio — Submission Form

### 1.What did you build, and what business outcome does it move?** State the number and the money.

Created a rule-based support ticket classifier and monthly reporting tool to categorize tickets based on customer messages, determine the team responsible for owning each ticket, and create charts, CSV reports, and a business case.

The total number of tickets for a period of January 2025 to June 2026 is 11,641, of which 875 are delivery related and 36.1% of the Billing tagged is delivery related. The aim is to lower this misrouting rate to less than 10%.

The average cost of handling each misrouted ticket is about ₹326 due to SLA breach credits and team transfers. Given the estimated ticket volume of 650 tickets per week, the estimated annual cost would be around ₹8.28 lakh. At the lower estimated volume of exports of around 150 per week, it is around ₹1.91 lakh. These are only estimates of savings, however, and do not guarantee anything.

### 2. What does one run cost, and what would a month cost at Vireo's volume (roughly 650 tickets a week)?** Show the arithmetic. If you used no paid calls, say so.?

It is run locally with python, pandas, matplotlib, and a simple regular expression. Does not use a paid API.

* Cost per run: ₹0 for paid API/service charges.
* Monthly volume: 650 tickets/week × 52 ÷ 12 ≈ 2,817 tickets/month.
* Monthly paid-call cost: 2,817 × ₹0 = ₹0.

This is excluding any costs of electricity, hardware or any subscription to an AI tool used during development. Any real AI subscription charges ought to be explicitly represented as another.

### 3. How do you know it works?** Sample size, how you checked, error rate, and the kind of case it gets wrong.?

A random sample of 50 Billing-tagged tickets was manually reviewed against the rule based classifier results. Of these 50 rules, 49 were correctly classified with 98% accuracy on this sample. The original bot assigned team had 50 tickets, and they got it right on 27 of those tickets, or 54%.

I also compared the team assignments made by the agent with the team assignments made by the classifier on 9,199 tickets that were classified by both methods, and found 89% team agreement.

The manual sample is a small sample and only reflects the accuracy of the Billing-tagged bucket and should not be used as a method to determine the accuracy of the other ticket categories. The tool can have difficulty with text that is too short or lack context, like a payment update that doesn't belong in that particular context. It would be useful to have more independent validation before using it for automated production routing.

### 4. Did you change, narrow, or push back on the client's ask?** What, when, and why. **[can only raise your score]?

Yes. Instead of immediately suggesting two hires for the biggest team, based on the volume of routed tickets, I did some research to see if the routing of the teams correlated with what customers were having problems with.

The analysis revealed that there were many ticket items in the Billing queue that were related to the delivery. So I came up with a solution, which I narrowed down to ticket classification, reporting of teams/categories, and a business case related to routing.

My initial suggestion is to make changes to how intakes are routed, track the outcomes for one month, and then evaluate workload and staffing requirements again. At this time, there is no data available to show that either team requires more players.

### 5. What is wrong with what you are handing us?** Be specific: bugs, shortcuts, things you know are off. **[can only raise your score]?

The classifier does not rely on a machine-learning model, but instead requires a set of ordered regular-expression rules. It might not perform well with other languages, multiple language messages, or confusing tickets.

Manual validation is limited to 50 Billing-tagged tickets, and was done by one person. The 89% agreement result is based on agent notes – these are not guaranteed to be correct.

Data transfer is only available for the helpdesk period from September 2025 onwards. The financial estimates are based on the assumed number of tickets and ticket price within the policy. The observed correlation between misrouting and SLA violations does not demonstrate that the violation of the SLAs is a direct result of misrouting.

Resolution-time analysis was not completed and a comprehensive audit of duplicate-reimport is not performed on the dataset. The tool is a prototype that is not fully validated and should be used as a decision support system.

### 6. What did you deliberately leave out, and why that rather than something else?

Tier-2 resolution-time analysis was not included, as the first work was on routing, team workload. I was not able to include lot-code defect analysis since the number of tickets per lot was too small to draw reliable conclusions.

I did not conduct a CSAT analysis, a detailed replacement versus refund audit was not done, and the number of conflicting cases identified was limited. I didn't make an LLM-based classifier because the simpler rules managed to get 98% accuracy in a small sample of the validation data, without requiring extra investments of API calls or complexity.

These decisions focused the work on the routing problem, but may merit investigation during a subsequent phase in the omitted areas.

### 7. Anything you built or found that nobody asked for?

I found a time stamp problem in the old data: The `resolved_at` data was in UTC, but the helpdesk timestamps were in local time. If the timezone correction wasn't applied, the number of tickets that looked like they had been solved before they were created would be 2,379. In addition, I threw out 139 stray legacy records in 2024 that didn't fit the analysis window.

Also, 921 warranty replacements were issued by tier-1 agents, which is not in line with the policy that mandates tier-2 approval for warranty replacement. I noted this because I wanted to find out more information, but not make any judgements about whether their replacements were appropriate.

### 8. What did you use AI for?** Which tools and models, where they helped, where they wasted your time, what you threw away. Link your three-minute screen recording here.?

ChatGPT and Claude were used on this assignment.

My use of ChatGPT was primarily to gain insights into the assignment's criteria, review the data and results, validate calculations with the output generated by the program, and formulate the business memo and submission-form answers. I used Claude Sonnet 5.5 via the claude.ai chat interface to assist with coding help with the classifier & analysis code, coding problems, and review of the 50-ticket validation sheet.

Both of these tools enabled me to understand the problem and to break through in the implementation. Some answers, however, required further checking or alteration to allow them to be fitted in with the actual data and requirements of the assignment. I double-checked the outputs and classified them where needed, and ensured that the number of figures provided in the memo matched the output. Set aside strategies that were too complicated and chose a rule-based classifier instead of an LLM-based classifier because it was simpler to run locally and required no paid API calls at runtime.

I did not treat AI-generated suggestions as automatically correct; I checked the results against the project outputs and my own manual review.

Tools used: GPT-5.6 Luna and Claude Sonnet 5.5.
Runtime API cost: ₹0; the tool makes no paid API calls.

Three-minute screen recording: https://www.loom.com/share/91b662c630354d518c47ec840c6f294a 

### 9.Someone picks this up on Monday and you are unreachable.** The three things they need to know?

From the project directory, run the following command: python src/run.py --data data --out out to re-generate the reports, charts and business-case outputs. The rules for classification are in src/classify.py.
The estimated financial impact is based on the assumed number of tickets per week and the cost of policy. Check the true volume and costs before relying on the estimates in a business decision.
After review and enhancement of intake-routing rules, review misrouting and SLA performance for a month and then reassess work load of the team.

### 10. Honest hours spent

4 hours 30 minutes (4.5 hours)

### 11. GitHub Repo Link

[https://github.com/Sindhu-patil224/vireo-support-ticket-analysis]