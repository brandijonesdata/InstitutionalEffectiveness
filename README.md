# Georgia Institutional Effectiveness Dashboard

An interactive decision-support dashboard for context-adjusted institutional benchmarking across Georgia four-year colleges and universities.

The dashboard was developed as part of:

**Beyond Rankings: Equity-Conscious Benchmarking of Student Success in Georgia Higher Education**

## Live dashboard

The public dashboard link will be added here after deployment:

`https://brandijonesdata/InstitutionalEffectivenessGA.streamlit.app`

## What the dashboard provides

Users can:

- Select a Georgia institution
- Compare observed completion with a context-based expected completion rate
- Review completion outperformance, defined as observed minus expected
- Examine Pell-equity outcomes and context-adjusted equity performance
- Review need-adjusted resource-adequacy indicators
- View empirical peer communities and institutional profiles
- Compare institutions across Georgia
- Download institution-level and filtered dashboard data

## Repository structure

```text
InstitutionalEffectiveness/
├── streamlit_app.py
├── requirements.txt
├── README.md
└── data/
    ├── georgia_dashboard_data.csv
    └── dashboard_build_audit.csv
```

## Dashboard measures

### Completion outperformance

```text
Completion outperformance =
Observed completion rate - Expected completion rate
```

Positive values indicate that the observed outcome exceeded the context-based expectation. Negative values indicate that the observed outcome was below expectation.

### Pell equity

Pell equity is expressed as the Pell-recipient outcome minus the corresponding non-Pell outcome.

- Positive values indicate a Pell advantage.
- Negative values indicate a Pell disadvantage.
- Values near zero indicate approximate parity.

### Resource adequacy

Resource-adequacy measures compare observed institutional resources with the level expected for institutional context and student need.

These measures are capacity proxies. They are not direct measures of instructional quality, service effectiveness, faculty satisfaction, or causal impact.

### Peer communities and institutional profiles

Peer communities were created from institutional-context similarities. Institutional profiles were created as a separate descriptive classification.

Peer relationships do not represent:

- Institutional rank
- Collaboration
- Transfer relationships
- Causal influence
- Institutional quality

## How to use the dashboard

### Sidebar controls

Use the sidebar to:

1. Filter institutions by public or private nonprofit control.
2. Filter by empirical peer community.
3. Filter by completion benchmark status.
4. Select an individual institution.
5. Download filtered Georgia data.

### Institution overview

The overview displays:

- Observed completion
- Context-expected completion
- Observed-minus-expected performance
- Resource adequacy
- Peer and profile information

### Georgia comparison

The Georgia comparison tab plots observed completion against expected completion.

- Institutions above the diagonal line have observed outcomes above expectation.
- Institutions below the diagonal line have observed outcomes below expectation.
- Hover over a point to view institutional details.

### Pell equity

The Pell-equity tab displays each institution's Pell-minus-non-Pell outcome and its context-adjusted equity results.

### Resources and strategy

This tab displays need-adjusted resource measures and the institution's strategic classification.

### Data and downloads

Users can review the full selected-institution record and download the available data.

## Interpretation

This dashboard is designed for diagnostic planning and institutional learning. It is not a punitive ranking system.

The results are institution-level predictive associations. They do not establish that a specific policy, expenditure, staffing level, or institutional characteristic caused an outcome.

Georgia institutions were excluded from national model fitting and were evaluated after the national benchmarking framework was locked.

## Data source

The dashboard uses 2024 Integrated Postsecondary Education Data System (IPEDS) institutional data.

The Georgia dashboard dataset includes observed and expected completion, completion outperformance, Pell equity, resource adequacy, empirical peer communities, and descriptive institutional profiles.

## Run locally

Install the dependencies:

```bash
pip install -r requirements.txt
```

Launch the application:

```bash
streamlit run streamlit_app.py
```

The application will open in a browser, usually at:

```text
http://localhost:8501
```

## Deploy with Streamlit Community Cloud

1. Sign in to Streamlit Community Cloud with GitHub.
2. Select **Create app**.
3. Choose the repository:
   `brandijonesdata/InstitutionalEffectiveness`
4. Select branch:
   `main`
5. Enter the main file path:
   `streamlit_app.py`
6. Select a Python version compatible with the requirements file.
7. Choose a custom subdomain if desired.
8. Select **Deploy**.

After deployment, update the **Live dashboard** section at the top of this README with the permanent Streamlit URL.

## Updating the dashboard

The GitHub repository is the source for the deployed application.

To update the dashboard:

1. Edit `streamlit_app.py`, the data file, or another repository file.
2. Commit the change to the `main` branch.
3. Streamlit Community Cloud will detect the commit and update the deployed application.

## Required Python packages

The application uses:

- Streamlit
- pandas
- NumPy
- Plotly

## Author

Brandi Jones  
Kennesaw State University  
Comprehensive Examination Project
