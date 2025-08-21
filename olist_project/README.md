# 📦 Olist Project

## 🚀 Project Overview

The **Olist Project** is an e-commerce data analysis and visualization project. It analyzes orders, delays, and regional distribution to uncover business insights.

**Key Questions:**
1. What % of orders are delivered late?
2. Which regions (states/cities) have the longest delivery times?
3. How do delivery delays affect customer review scores?
4. Which product categories generate the highest revenue?
5. Which sellers have the highest sales volume and best customer ratings?

**Workflow:**

* Load raw data into **PostgreSQL**
* Analyze data using **SQL**
* Visualize results with **Power BI** (PDF export)

## 🛠 Tech Stack

* **Database:** PostgreSQL (Docker Compose)
* **Data Loading:** Python (`load_data_into_postgres.py`)
* **Data Analysis:** SQL
* **Visualization:** Power BI (PDF export)
* **Dependency Management:** `.gitignore`

## 📁 Project Structure

* `sql/`

  * `late_orders.sql` — Analyze delayed orders
  * `delay_by_state.sql` — Analyze delays by state
  * Other SQL scripts
* `docker-compose.yml` — PostgreSQL configuration
* `load_data_into_postgres.py` — Python data loader
* `log.md` — Notes
* `olist-analysis.pdf` — Power BI exported PDFs
* `.gitignore` — Ignored files
* `README.md` — Project documentation

## 🔍 Data Analysis Workflow

1. **Set up the Database**

```bash
docker-compose up -d
```

2. **Load Data**

```bash
python load_data_into_postgres.py
```

3. **SQL Analysis**

```sql
\i sql/late_orders.sql;
\i sql/delay_by_state.sql;
```

4. **Visualization**

* Import SQL query results into Power BI
* Create dashboards
* Export as PDF into `visualization/`

## 📊 Data Source

* [Olist Brazilian E-commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
* Includes orders, customers, products, and geographical information

## ⚠️ Notes

* Power BI Desktop cannot generate shareable links; use PDF for visualization
* Ensure PostgreSQL credentials in `load_data_into_postgres.py` are correct
* Maintain the project folder structure for smooth execution

## 🤝 Contributing

* Fork the repository
* Submit changes via Pull Request

## 📄 License

MIT License
