# Athena Voice — Demo Script
### NLP-to-SQL Analytics for Apple Retail Data

---

## Opening (30 seconds)

> "Hi everyone, we're presenting **Athena Voice** — an AI-powered analytics assistant that lets anyone query Apple's retail sales data using plain English or voice, and get instant results from a real data lake."
>
> "No SQL knowledge needed. Ask a question, get the answer — with the SQL, data table, and an AI-generated summary."

---

## 1. Login & Role-Based Access (30 seconds)

**Action:** Show the login screen.

> "The app starts with a secure login. We have role-based access control — different users can access different tables."

**Action:** Click one of the demo account shortcuts (e.g., `admin`).

> "For the demo, we'll log in as admin who has access to all five tables: sales, products, stores, categories, and warranty."

**Action:** Click the user profile button (top-right) to show the role badge and accessible tables.

> "The profile shows the user's role and exactly which tables they're authorized to query."

---

## 2. Simple Question — Text Input (60 seconds)

**Action:** Type: `What are the top selling products?`

> "Let's start simple. I'll type a natural language question — 'What are the top selling products?'"

**Wait for response.**

> "Behind the scenes, here's what happened:
> 1. Our **Strands AI Agent** analyzed the question and picked the best tool from 15 predefined SQL tools
> 2. The tool generated a **Trino-compatible SQL query** with proper joins across our sales and products tables
> 3. The query ran on **Amazon Athena** against over 1 million sales records in S3
> 4. Results came back and **Claude on Bedrock** generated a natural language summary"

**Action:** Expand the SQL display to show the generated query.

> "You can see the exact SQL that was generated — fully transparent. It joined sales with products and categories, aggregated by units sold, and returned the top 10."

**Action:** Point to the data table.

> "Here are the results in a clean table — with row count, execution time, and estimated query cost."

**Action:** Point to the summary card.

> "And here's the AI summary explaining the key takeaways in plain English."

---

## 3. Voice Input (45 seconds)

**Action:** Click the microphone push-to-talk button and speak: "Show me store performance in Japan"

> "Now let's try voice. I'll hold the mic button and ask — 'Show me store performance in Japan'"

**Wait for response.**

> "Same flow — but this time triggered by voice using the Web Speech API. The agent picked our store performance tool, filtered to Japan, and returned per-store metrics: revenue, units sold, avg order quantity, and transactions."

---

## 4. Complex Analytics Query (45 seconds)

**Action:** Type: `Compare year-over-year sales growth between 2023 and 2024 for the United States in the Laptop category`

> "Let's try something more complex — a year-over-year comparison. This is the kind of query that would normally take an analyst 10 minutes to write in SQL."

**Wait for response.**

> "The agent selected our YoY growth tool, passed in both years, the country, and category as parameters. The SQL uses CASE expressions to calculate revenue for each year, computes the growth delta, and shows the percentage change."

---

## 5. Warranty / Quality Query (30 seconds)

**Action:** Type: `What is the average days between sale and warranty claim for Smartphone products?`

> "We also have warranty data. This question asks about mean-time-to-failure patterns — how quickly products get warranty claims after being sold."

**Wait for response.**

> "The SQL uses Trino's date_diff function to calculate days between sale date and claim date, then averages by product. Quality teams can use this to identify products that fail quickly."

---

## 6. Export & Share (20 seconds)

**Action:** Click the CSV download button on the results table.

> "Users can download results as CSV for further analysis in Excel."

**Action:** Click the email button and show the email modal.

> "Or email the results directly to a colleague — it shows a preview of what will be sent."

---

## 7. Dark Mode (10 seconds)

**Action:** Toggle dark mode.

> "And of course, dark mode — because every good analytics tool needs one."

---

## Architecture Slide (45 seconds)

> "Let me quickly walk through the architecture:
>
> - **Frontend**: React with Chakra UI — voice and text input, responsive design
> - **Backend**: FastAPI serving a REST API at `/api/v1/ask`
> - **AI Agent**: Strands Agent with 15 predefined MCP tools + a fallback SQL generator — all with the full database schema embedded so the LLM always generates correct SQL
> - **Query Engine**: Amazon Athena running Trino SQL over Parquet files in S3
> - **Data**: 1M+ sales transactions, 89 products, 75 stores across 19 countries, 30K warranty claims
> - **Summarization**: Claude 3 on AWS Bedrock generates plain English insights
> - **Security**: SQL governance layer blocks dangerous operations (DROP, DELETE, etc.), enforces table whitelist, estimates query cost before execution"

---

## Key Differentiators (20 seconds)

> "What makes this stand out:
> 1. **MCP Tools over pure LLM** — 15 prebuilt, validated SQL patterns mean faster and more reliable results than raw LLM generation
> 2. **Governance built-in** — every query is validated for safety and cost before execution
> 3. **Voice-first** — designed for managers and execs who don't write SQL
> 4. **Fully transparent** — users see the SQL, data, and can verify everything"

---

## Closing (15 seconds)

> "That's **Athena Voice** — turning natural language into real-time retail insights from a production AWS data lake. Thank you!"

---

## Backup Questions & Queries

If asked to demo more, use these:

| Question | Tool Hit |
|----------|----------|
| "Show total revenue by country for 2023" | Q01 - total_sales_revenue_by_country |
| "Top 5 Audio products by units sold" | Q02 - top_products_by_category |
| "Monthly sales trend for iPhone 14 Pro" | Q04 - monthly_sales_trend_by_product |
| "Products launched after 2023 in the Wearable category" | Q07 - new_product_launch_performance |
| "Revenue share of each product in the Laptop category for 2023" | Q09 - product_revenue_share_in_category |
| "Quarterly sales for Apple Fifth Avenue in 2023" | Q10 - quarterly_store_sales_summary |
| "Rank cities in the United States by revenue for 2023" | Q12 - city_sales_ranking_by_country |
| "Category sales breakdown for Apple Fifth Avenue" | Q14 - store_category_sales_mix |
| "Transactions over $10,000 in Germany" | Q15 - high_value_transactions |

---

**Total demo time: ~5–6 minutes**
