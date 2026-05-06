import marimo

__generated_with = "0.19.2"
app = marimo.App(width="medium")


@app.cell
def _():
    #can adjust according to your own path
    file_path = r"C:\Users\leeze\Documents\GitHub\Li_Zexuan\Visual_Group\MC1-data\MC1_graph.json"
    import marimo as mo
    import networkx as nx
    import json
    import pandas as pd
    import altair as alt
    from sklearn.preprocessing import StandardScaler
    import numpy as np


    # Load data
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Create graph
    G = nx.node_link_graph(data, edges='links')

    print(f"Nodes: {G.number_of_nodes():,}")
    print(f"Edges: {G.number_of_edges():,}")

    # Convert node data to a DataFrame
    nodes_data = []
    for node_id, attrs in G.nodes(data=True):
        nodes_data.append({'node_id': node_id, **attrs})
    nodes_df = pd.DataFrame(nodes_data)

    print("\nDataFrame columns:", nodes_df.columns.tolist())

    # Convert edge data to a DataFrame
    edges_data = []
    for u, v, attrs in G.edges(data=True):
        edges_data.append({
            'source': u,
            'target': v,
            **attrs
        })
    edges_df = pd.DataFrame(edges_data)

    print(f"Edge DataFrame shape: {edges_df.shape}")
    print(f"Columns: {edges_df.columns.tolist()}")
    print(f"\nEdge type distribution:\n{edges_df['Edge Type'].value_counts()}")

    # Check for "Sailor Shift"
    sailor = nodes_df[nodes_df['name'] == 'Sailor Shift']
    if len(sailor) > 0:
        print(sailor[['node_id', 'name', 'Node Type']])
        sailor_id = sailor.iloc[0]['node_id']

        # Inspect Sailor Shift's connections
        sailor_edges = edges_df[
            (edges_df['source'] == sailor_id) | 
            (edges_df['target'] == sailor_id)
        ]
        print(f"\nSailor connections: {len(sailor_edges)}")
        print(f"Connection types:\n{sailor_edges['Edge Type'].value_counts()}")
    else:
        print("Sailor Shift not found")
        persons = nodes_df[nodes_df['Node Type'] == 'Person']
        print("\nSample persons (top 5):")
        print(persons[['name']].head())
    return G, StandardScaler, alt, edges_df, mo, nodes_df, np, pd, sailor_id


@app.cell
def _(G, StandardScaler, edges_df, nodes_df, np, pd, sailor_id):
    pd.set_option('future.no_silent_downcasting', True)

    # 1. Standardize column names (convert to lowercase for consistency)
    nodes_df.columns = [c.lower().replace(' ', '_') for c in nodes_df.columns]
    edges_df.columns = [c.lower().replace(' ', '_') for c in edges_df.columns]

    print("\n1. Column names standardized:")
    print(f"Node columns: {nodes_df.columns.tolist()}")
    print(f"Edge columns: {edges_df.columns.tolist()}")

    # 2. Process time-related columns
    print("\n2. Processing time-related columns")
    nodes_df['release_year'] = pd.to_numeric(nodes_df['release_date'], errors='coerce')
    nodes_df['notoriety_year'] = pd.to_numeric(nodes_df['notoriety_date'], errors='coerce')
    nodes_df['written_year'] = pd.to_numeric(nodes_df['written_date'], errors='coerce')

    print(f"Year range: {nodes_df['release_year'].min():.0f} - {nodes_df['release_year'].max():.0f}")

    # 3. Process boolean variables
    print("\n3. Processing boolean variables")
    nodes_df['notable'] = nodes_df['notable'].fillna(False).astype(bool)
    nodes_df['single'] = nodes_df['single'].fillna(False).astype(bool)

    print(f"Notable count: {nodes_df['notable'].sum()}")
    print(f"Single count: {nodes_df['single'].sum()}")

    # 4. Handle categorical variables
    print("\n4. Handling categorical variables")
    nodes_df['genre'] = nodes_df['genre'].fillna('Unknown')
    nodes_df['stage_name'] = nodes_df['stage_name'].fillna('')
    nodes_df['name'] = nodes_df['name'].fillna('Unknown')

    # 5. Compute network metrics
    print("\n5. Computing degree metrics")
    degree_dict = dict(G.degree())
    nodes_df['degree'] = nodes_df['node_id'].map(degree_dict)

    # Compute degree per edge type (incoming and outgoing)
    for edge_type in edges_df['edge_type'].unique():
        source_counts = edges_df[edges_df['edge_type'] == edge_type].groupby('source').size()
        nodes_df[f'source_{edge_type.lower()}_count'] = nodes_df['node_id'].map(source_counts).fillna(0)

        target_counts = edges_df[edges_df['edge_type'] == edge_type].groupby('target').size()
        nodes_df[f'target_{edge_type.lower()}_count'] = nodes_df['node_id'].map(target_counts).fillna(0)

    print(f"Degree range: {nodes_df['degree'].min()} - {nodes_df['degree'].max()}")

    # 6. Compute collaboration and influence metrics
    print("\n6. Computing collaboration and influence metrics")

    # Collaboration count (for all nodes)
    collab_types = ['performerof', 'composerof', 'producerof', 'lyricistof']
    nodes_df['collaboration_count'] = 0

    for ctype in collab_types:
        source_col = f'source_{ctype}_count'
        target_col = f'target_{ctype}_count'

        if source_col in nodes_df.columns:
            nodes_df['collaboration_count'] += nodes_df[source_col]
        if target_col in nodes_df.columns:
            nodes_df['collaboration_count'] += nodes_df[target_col]

    # Influence metrics
    influence_types = {
        'influence_out': [
            'source_instyleof_count', 'source_lyricalreferenceto_count',
            'source_interpolatesfrom_count', 'source_coverof_count',
            'source_directlysamples_count'
        ],
        'influence_in': [
            'target_instyleof_count', 'target_lyricalreferenceto_count',
            'target_interpolatesfrom_count', 'target_coverof_count',
            'target_directlysamples_count'
        ]
    }

    for direction, cols in influence_types.items():
        nodes_df[direction] = 0
        for col in cols:
            if col in nodes_df.columns:
                nodes_df[direction] += nodes_df[col]

    # 7. Handle missing values
    print("\n7. Handling missing values")
    numeric_cols = nodes_df.select_dtypes(include=[np.number]).columns
    nodes_df[numeric_cols] = nodes_df[numeric_cols].fillna(0)

    remaining_nulls = nodes_df.isnull().sum().sum()
    print(f"Remaining missing values: {remaining_nulls}")

    # 8. Standardize features and display results
    print("\n8. Feature standardization")
    cols_to_scale = ['degree', 'collaboration_count', 'influence_out', 'influence_in']
    existing_cols = [col for col in cols_to_scale if col in nodes_df.columns]

    if existing_cols:
        scaler = StandardScaler()
        nodes_df[[f'{col}_scaled' for col in existing_cols]] = scaler.fit_transform(
            nodes_df[existing_cols]
        )
        print(f"Standardized columns: {existing_cols}")

        # Display results for Sailor Shift
        sailor_data = nodes_df[nodes_df['node_id'] == sailor_id].iloc[0]
        print("\n=== Sailor Shift ===")
        print(f"Degree: {sailor_data['degree']}")
        print(f"Collaborations: {sailor_data['collaboration_count']}")
        print(f"Influence on others: {sailor_data['influence_out']}")
        print(f"Influenced by others: {sailor_data['influence_in']}")

    # 9. Extract Sailor Shift's ego network
    print("\n9. Extracting Sailor Shift ego network")

    sailor_neighbors = list(G.neighbors(sailor_id))
    sailor_ego_nodes = [sailor_id] + sailor_neighbors
    sailor_ego_df = nodes_df[nodes_df['node_id'].isin(sailor_ego_nodes)]

    sailor_ego_edges = edges_df[
        (edges_df['source'] == sailor_id) |
        (edges_df['target'] == sailor_id) |
        (
            edges_df['source'].isin(sailor_neighbors) &
            edges_df['target'].isin(sailor_neighbors)
        )
    ]

    print(f"Ego network size: {len(sailor_ego_df)} nodes, {len(sailor_ego_edges)} edges")

    print("\nFinal shape:")
    print(f"Nodes: {nodes_df.shape}")
    print(f"Edges: {edges_df.shape}")
    return


@app.cell
def _(mo):
    mo.md(r"""
    2a.Was this influence intermittent or did it have a gradual rise?
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    2b.What genres and top artists have been most influenced by Oceanus Folk?
    """)
    return


@app.cell
def _(nodes_df):
    # Filter Oceanus Folk works (songs and albums)
    of_works = nodes_df[
        (nodes_df['genre'] == 'Oceanus Folk') &
        (nodes_df['node_type'].isin(['Song', 'Album']))
    ]

    # Extract node IDs
    of_ids = of_works['node_id'].tolist()

    # Display dataset overview
    print("=" * 50)
    print("Oceanus Folk Dataset Overview")
    print("=" * 50)

    print(f"Total works: {len(of_works)}")
    print(f"Year range: {of_works['release_year'].min():.0f} - {of_works['release_year'].max():.0f}")
    print(f"Number of songs: {len(of_works[of_works['node_type'] == 'Song'])}")
    print(f"Number of albums: {len(of_works[of_works['node_type'] == 'Album'])}")
    return (of_ids,)


@app.cell
def _(alt, edges_df, mo, nodes_df, of_ids, pd):
    # ============================================================================
    # 1. Identify edges where Oceanus Folk works influence other genres
    # ============================================================================
    of_out_edges = edges_df[
        (edges_df['source'].isin(of_ids)) &
        (edges_df['edge_type'].isin([
            'InStyleOf', 'CoverOf', 'DirectlySamples',
            'InterpolatesFrom', 'LyricalReferenceTo'
        ]))
    ]

    print(f"OF influence edges: {len(of_out_edges)}")
    print(f"OF works: {len(of_ids)}")

    # ============================================================================
    # 2. Extract influenced works with genre and year
    # ============================================================================
    of_out_targets = nodes_df[
        nodes_df['node_id'].isin(of_out_edges['target'])
    ][['node_id', 'genre', 'release_year']].copy()

    # Exclude Oceanus Folk and missing years
    of_out_targets = of_out_targets[
        (of_out_targets['genre'] != 'Oceanus Folk') &
        (of_out_targets['release_year'].notna())
    ]

    # Keep year as integer (not string)
    of_out_targets['year'] = of_out_targets['release_year'].astype(int)

    print(f"Unique influenced works: {len(of_out_targets)}")

    # ============================================================================
    # 3. Figure 1: Stacked area chart (annual influence by genre)
    # ============================================================================
    # Aggregate influence over time by genre
    of_out_stacked = of_out_targets.groupby(['year', 'genre'])['node_id'].count().reset_index()
    of_out_stacked.columns = ['year', 'genre', 'count']

    # Select top 6 genres overall
    of_out_top_genres = (
        of_out_stacked.groupby('genre')['count']
        .sum()
        .nlargest(6)
        .index
        .tolist()
    )

    # Group remaining genres as "Other"
    of_out_stacked['genre_grouped'] = of_out_stacked['genre'].apply(
        lambda x: x if x in of_out_top_genres else 'Other'
    )

    of_out_stacked2 = (
        of_out_stacked.groupby(['year', 'genre_grouped'])['count']
        .sum()
        .reset_index()
    )

    # ============================================================================
    # 4. Figure 2: Genre bar chart
    # ============================================================================
    of_out_genre_counts = of_out_targets['genre'].value_counts().reset_index()
    of_out_genre_counts.columns = ['genre', 'count']
    of_out_genre_counts = of_out_genre_counts.head(10)

    of_out_genre_counts['genre_grouped'] = of_out_genre_counts['genre'].apply(
        lambda x: x if x in of_out_top_genres else 'Other'
    )

    # ============================================================================
    # 5. Figure 3: Artist influence analysis (with deduplication)
    # ============================================================================
    # Get unique influenced works (deduplicate to avoid double counting)
    of_unique_targets = of_out_edges[['target']].drop_duplicates()
    of_unique_targets.columns = ['work_id']

    # Find performing artists for these works
    of_out_perf = edges_df[
        (edges_df['target'].isin(of_unique_targets['work_id'])) &
        (edges_df['edge_type'] == 'PerformerOf')
    ][['source', 'target']].rename(
        columns={'source': 'artist_id', 'target': 'work_id'}
    )

    # Keep only person nodes
    of_out_perf = of_out_perf[
        of_out_perf['artist_id'].isin(nodes_df[nodes_df['node_type'] == 'Person']['node_id'])
    ]

    # Count influences per artist (each influenced work counted once)
    of_out_artist_counts = (
        of_out_perf.groupby('artist_id')['work_id']
        .nunique()
        .reset_index(name='total')
    )

    # Merge with artist names
    of_out_artist_top = of_out_artist_counts.merge(
        nodes_df[['node_id', 'name']].rename(columns={'node_id': 'artist_id'}),
        on='artist_id'
    )

    # Determine each artist's main genre
    of_out_artist_works = edges_df[
        (edges_df['source'].isin(of_out_artist_top['artist_id'])) &
        (edges_df['edge_type'] == 'PerformerOf')
    ]

    of_out_artist_work_genres = nodes_df[
        nodes_df['node_id'].isin(of_out_artist_works['target'])
    ][['node_id', 'genre']].drop_duplicates()

    of_out_artist_works2 = of_out_artist_works.merge(
        of_out_artist_work_genres,
        left_on='target',
        right_on='node_id'
    )

    of_out_artist_genre = (
        of_out_artist_works2.groupby('source')['genre']
        .agg(lambda x: x.value_counts().index[0])
        .reset_index()
    )
    of_out_artist_genre.columns = ['artist_id', 'main_genre']

    # Merge and filter
    of_out_artist_df = of_out_artist_top.merge(of_out_artist_genre, on='artist_id')
    of_out_artist_df = of_out_artist_df[of_out_artist_df['main_genre'] != 'Oceanus Folk']

    # Group genres
    of_out_artist_df['genre_grouped'] = of_out_artist_df['main_genre'].apply(
        lambda x: x if x in of_out_top_genres else 'Other'
    )

    # Top 3 artists per genre
    of_out_artist_grouped = (
        of_out_artist_df
        .sort_values(['genre_grouped', 'total'], ascending=[True, False])
        .groupby('genre_grouped', as_index=False)
        .head(3)
        .reset_index(drop=True)
    )

    # Convert types
    of_out_stacked2['genre_grouped'] = of_out_stacked2['genre_grouped'].astype(str)
    of_out_genre_counts['genre_grouped'] = of_out_genre_counts['genre_grouped'].astype(str)
    of_out_artist_grouped['genre_grouped'] = of_out_artist_grouped['genre_grouped'].astype(str)

    # ============================================================================
    # 6. Selection for all charts
    # ============================================================================
    of_out_selection = alt.selection_point(
        fields=['genre_grouped'],
        bind='legend'
    )

    # ============================================================================
    # 7. Chart 1: Stacked area chart with breakthrough annotation
    # ============================================================================
    of_out_chart_area = alt.Chart(of_out_stacked2).mark_area(opacity=0.8).encode(
        x=alt.X('year:Q', title='Year', axis=alt.Axis(format='d')),
        y=alt.Y('count:Q', stack='zero', title='Works Influenced by Oceanus Folk'),
        color=alt.Color('genre_grouped:N', title='Genre'),
        opacity=alt.condition(of_out_selection, alt.value(1), alt.value(0.2)),
        tooltip=['year', 'genre_grouped', 'count']
    ).add_params(of_out_selection).properties(
        title='Spread of Oceanus Folk Influence Over Time by Genre',
        width=620,
        height=280
    )

    # Add vertical line for 2028
    breakthrough_line = alt.Chart(pd.DataFrame({'year': [2028]})).mark_rule(
        color='red',
        strokeDash=[5, 5],
        strokeWidth=2
    ).encode(x='year:Q')

    # Add annotation text
    if 2028 in of_out_stacked2['year'].values:
        max_count = of_out_stacked2[of_out_stacked2['year'] == 2028]['count'].max()
    else:
        max_count = 50

    annotation_text = alt.Chart(pd.DataFrame({
        'year': [2028],
        'count': [max_count],
        'text': ["Sailor's Breakthrough (2028)"]
    })).mark_text(
        align='left',
        baseline='top',
        dx=10,
        dy=-5,
        fontSize=11,
        color='red'
    ).encode(
        x='year:Q',
        y='count:Q',
        text='text'
    )

    of_out_chart_area_annotated = of_out_chart_area + breakthrough_line + annotation_text

    # ============================================================================
    # 8. Chart 2: Genre bar chart
    # ============================================================================
    of_out_chart_bar = alt.Chart(of_out_genre_counts).mark_bar().encode(
        x=alt.X('count:Q', title='Number of Works'),
        y=alt.Y('genre_grouped:N', sort='-x', title='Genre'),
        color=alt.condition(
            of_out_selection,
            alt.Color('genre_grouped:N', legend=None),
            alt.value('lightgray')
        ),
        tooltip=['genre', 'count']
    ).properties(
        title='Genres Most Influenced by Oceanus Folk',
        width=400,
        height=280
    )

    # ============================================================================
    # 9. Chart 3: Artist bar chart
    # ============================================================================
    of_out_chart_artist = alt.Chart(of_out_artist_grouped).mark_bar().encode(
        x=alt.X('total:Q', title='Number of Influenced Works'),
        y=alt.Y('name:N', sort='-x', title='Artist'),
        color=alt.condition(
            of_out_selection,
            alt.Color('genre_grouped:N', legend=None),
            alt.value('lightgray')
        ),
        tooltip=['name', 'genre_grouped', 'total']
    ).properties(
        title='Top Artists Influenced by Oceanus Folk',
        width=400,
        height=280
    )

    # ============================================================================
    # 10. Combine all charts
    # ============================================================================
    of_out_combined = of_out_chart_area_annotated & (of_out_chart_bar | of_out_chart_artist)

    mo.ui.altair_chart(of_out_combined)
    return of_out_edges, of_out_targets


@app.cell
def _(alt, nodes_df, of_out_edges, pd):
    # Use unique influenced works to avoid double counting
    c_of_influence = of_out_edges[['target']].drop_duplicates().merge(
        nodes_df[['node_id', 'release_year']].rename(columns={'node_id': 'target'}),
        on='target',
        how='left'
    )

    c_of_influence = c_of_influence[c_of_influence['release_year'].notna()]
    c_of_influence['year'] = c_of_influence['release_year'].astype(int)

    # Group by year and count UNIQUE works influenced
    c_of_yearly = c_of_influence.groupby('year').size().reset_index(name='count')
    c_of_yearly = c_of_yearly.sort_values('year')

    # Calculate cumulative
    c_of_yearly['cumulative'] = c_of_yearly['count'].cumsum()

    # Add period classification
    c_of_yearly['period'] = c_of_yearly['year'].apply(
        lambda x: 'After 2028' if x >= 2028 else 'Before 2028'
    )

    print("=== Cumulative Influence Summary ===")
    print(f"Total unique works influenced: {c_of_yearly['cumulative'].iloc[-1]}")
    print(f"Year range: {c_of_yearly['year'].min()} - {c_of_yearly['year'].max()}")
    print(f"Before 2028 average: {c_of_yearly[c_of_yearly['year'] < 2028]['count'].mean():.1f} works/year")
    print(f"After 2028 average: {c_of_yearly[c_of_yearly['year'] >= 2028]['count'].mean():.1f} works/year")
    print("\nYearly breakdown:")
    print(c_of_yearly)

    # Create cumulative line chart
    c_of_cumulative_chart = alt.Chart(c_of_yearly).mark_line(
        color='#e07b39',
        strokeWidth=3,
        point=alt.OverlayMarkDef(filled=True, fill='white', size=60)
    ).encode(
        x=alt.X('year:Q', title='Year', axis=alt.Axis(format='d')),
        y=alt.Y('cumulative:Q', title='Cumulative Number of Works Influenced by Oceanus Folk'),
        tooltip=['year', 'cumulative', 'count']
    ).properties(
        title='Oceanus Folk Influence: Cumulative Growth Over Time',
        width=600,
        height=400
    )

    # Add vertical line for 2028
    c_of_breakthrough_line = alt.Chart(pd.DataFrame({'year': [2028]})).mark_rule(
        color='red',
        strokeDash=[5, 5],
        strokeWidth=2
    ).encode(x='year:Q')

    # Add annotation
    if 2028 in c_of_yearly['year'].values:
        c_of_2028_value = c_of_yearly[c_of_yearly['year'] == 2028]['cumulative'].iloc[0]
    else:
        c_of_2028_value = 100

    c_of_annotation = alt.Chart(pd.DataFrame({
        'year': [2028],
        'cumulative': [c_of_2028_value],
        'text': ["Sailor's Breakthrough (2028)"]
    })).mark_text(
        align='left',
        baseline='top',
        dx=10,
        dy=-10,
        fontSize=11,
        color='red'
    ).encode(
        x='year:Q',
        y='cumulative:Q',
        text='text'
    )

    c_of_final_chart = c_of_cumulative_chart + c_of_breakthrough_line + c_of_annotation

    # ===== Annual New Works Chart =====
    c_annual_chart = alt.Chart(c_of_yearly).mark_bar().encode(
        x=alt.X('year:Q', title='Year', axis=alt.Axis(format='d')),
        y=alt.Y('count:Q', title='New Works Influenced per Year'),
        color=alt.Color('period:N', title='Period',
                        scale=alt.Scale(domain=['Before 2028', 'After 2028'],
                                        range=['#aec7e8', '#e07b39'])),
        tooltip=['year', 'count', 'cumulative']
    ).properties(
        title='Annual New Works Influenced by Oceanus Folk',
        width=600,
        height=400
    )


    c_of_final_chart | c_annual_chart
    return (c_of_yearly,)


@app.cell
def _():
    return


@app.cell
def _(of_out_targets):
    # 查看 of_out_targets 的年份分布
    print("=== 被OF影响的作品年份分布 ===")
    print(of_out_targets.groupby('year').size().sort_index())

    # 查看总的唯一作品数
    print(f"\n=== 总计 ===")
    print(f"唯一被OF影响的作品数: {of_out_targets['node_id'].nunique()}")
    print(f"年份范围: {of_out_targets['year'].min()} - {of_out_targets['year'].max()}")
    return


@app.cell
def _(of_out_targets):
    print("=== Check of_out_targets ===")
    print(f"Total rows: {len(of_out_targets)}")
    print(f"Year range: {of_out_targets['year'].min()} - {of_out_targets['year'].max()}")
    print(f"\nFirst 20 rows:")
    print(of_out_targets[['year', 'genre']].head(20))
    print(f"\nYearly counts:")
    print(of_out_targets.groupby('year').size().sort_index())
    return


@app.cell
def _(c_of_yearly):
    # 查看2023年前后数据
    c_of_yearly[c_of_yearly['year'].between(2020, 2035)]
    return


@app.cell
def _(edges_df, nodes_df, of_ids):
    # Identify edges where Oceanus Folk is influenced by other genres
    of_inspired_edges = edges_df[
        (edges_df['target'].isin(of_ids)) &
        (edges_df['edge_type'].isin([
            'InStyleOf', 'CoverOf', 'DirectlySamples',
            'InterpolatesFrom', 'LyricalReferenceTo'
        ]))
    ]

    # Extract source nodes (influencing works) with genre and release year
    of_inspired_sources = nodes_df[
        nodes_df['node_id'].isin(of_inspired_edges['source'])
    ][['node_id', 'genre', 'release_year']]

    # Exclude Oceanus Folk and missing values
    of_inspired_sources = of_inspired_sources[
        (of_inspired_sources['genre'] != 'Oceanus Folk') &
        (of_inspired_sources['release_year'].notna())
    ]

    # Split into periods before and after Sailor Shift's breakthrough
    of_inspired_sources['period'] = of_inspired_sources['release_year'].apply(
        lambda x: 'After 2028' if x >= 2028 else 'Before 2028'
    )

    # Aggregate counts by period and genre
    of_period = (
        of_inspired_sources
        .groupby(['period', 'genre'])['node_id']
        .count()
        .reset_index()
    )

    of_period.columns = ['period', 'genre', 'count']

    # Display top results
    print(of_period.sort_values('count', ascending=False).head(20))

    of_period
    return


@app.cell
def _(c_of_yearly):
    # 查看2023年前后数据
    c_of_yearly[c_of_yearly['year'].between(2020, 2035)]
    return


@app.cell
def _():
    #1a
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Task 1a — Who has Sailor Shift been most influenced by over time?
    """)
    return


@app.cell
def _(influence_df, sailor_in_edges, sailor_works):
    print("Sailor works:", len(sailor_works))
    print("Influence edges:", len(sailor_in_edges))
    print("After merge:", len(influence_df))
    return


@app.cell
def _(edges_df, sailor_id):
    edges_df[edges_df['source'] == sailor_id]['edge_type'].value_counts()
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Task 1a — Who has Sailor Shift been most influenced by over time?
    """)
    return


@app.cell
def _(edges_df, nodes_df, sailor_id):
    # ================================================================

    # TASK 1a  —  Sailor's influences, anchored to her release years

    #

    # Every influencing artist appears exactly once, so artist-level

    # charts are flat. The meaningful dimensions are:

    #   - GENRE of the work she drew from

    #   - EDGE TYPE (CoverOf, InStyleOf, etc.) — how she drew from it

    #   - AGE of the source (how old was the work she referenced?)

    #   - YEAR of HER work that contains the reference

    # ================================================================


    a_collab_types    = ['PerformerOf', 'ComposerOf', 'ProducerOf', 'LyricistOf']

    a_influence_types = ['InStyleOf', 'CoverOf', 'DirectlySamples',

                         'InterpolatesFrom', 'LyricalReferenceTo']


    # Sailor's own works with release year

    a_sailor_works = (

        edges_df[

            (edges_df['source'] == sailor_id) &

            (edges_df['edge_type'].isin(a_collab_types))

        ][['target']]

        .merge(

            nodes_df[['node_id', 'name', 'release_year']].rename(

                columns={'node_id': 'target', 'name': 'sailor_work_name'}),

            on='target', how='left'

        )

        .dropna(subset=['release_year'])

        .rename(columns={'target': 'sailor_work_id'})

    )

    a_sailor_works['sailor_year'] = a_sailor_works['release_year'].astype(int)

    a_sailor_works = a_sailor_works[a_sailor_works['sailor_year'] > 0]


    # Outgoing influence edges from Sailor's works

    a_influence_edges = edges_df[

        (edges_df['source'].isin(a_sailor_works['sailor_work_id'])) &

        (edges_df['edge_type'].isin(a_influence_types))

    ][['source', 'target', 'edge_type']].rename(

        columns={'source': 'sailor_work_id', 'target': 'ref_work_id',

                 'edge_type': 'inf_type'}

    )


    # Attach Sailor's work year

    a_influence_edges = a_influence_edges.merge(

        a_sailor_works[['sailor_work_id', 'sailor_year', 'sailor_work_name']],

        on='sailor_work_id', how='left'

    )


    # Attach referenced work info (genre, release year, name)

    a_ref_info = nodes_df[['node_id', 'name', 'genre', 'release_year']].rename(

        columns={'node_id': 'ref_work_id', 'name': 'ref_name',

                 'release_year': 'ref_year'}

    )

    a_influence_edges = a_influence_edges.merge(a_ref_info, on='ref_work_id', how='left')

    a_influence_edges = a_influence_edges.dropna(subset=['ref_year'])

    a_influence_edges['ref_year'] = a_influence_edges['ref_year'].astype(int)

    a_influence_edges = a_influence_edges[a_influence_edges['ref_year'] > 0]


    # Source age when Sailor referenced it

    a_influence_edges['source_age'] = (

        a_influence_edges['sailor_year'] - a_influence_edges['ref_year']

    )


    # Genre grouping — collapse rare genres into 'Other'

    a_top_genres = (

        a_influence_edges['genre']

        .value_counts()

        .nlargest(7)

        .index.tolist()

    )

    a_influence_edges['genre_grouped'] = a_influence_edges['genre'].apply(

        lambda g: g if g in a_top_genres else 'Other'

    )


    print(f"Total influence references: {len(a_influence_edges)}")

    print(f"\nBy genre:\n{a_influence_edges['genre'].value_counts()}")

    print(f"\nBy influence type:\n{a_influence_edges['inf_type'].value_counts()}")

    print(f"\nBy Sailor's work year:\n{a_influence_edges['sailor_year'].value_counts().sort_index()}")

    print(f"\nSource age stats:\n{a_influence_edges['source_age'].describe()}")


    # ── Aggregations for charts ──────────────────────────────────────


    # 1. Genre × year (Sailor's work year)

    a_genre_yr = (

        a_influence_edges.groupby(['sailor_year', 'genre_grouped'])

        .size().reset_index(name='count')

    )

    a_genre_yr['year'] = a_genre_yr['sailor_year'].astype(str)


    # 2. Influence type × year

    a_type_yr = (

        a_influence_edges.groupby(['sailor_year', 'inf_type'])

        .size().reset_index(name='count')

    )

    a_type_yr['year'] = a_type_yr['sailor_year'].astype(str)


    # 3. Source age distribution per year

    a_age_yr = a_influence_edges[['sailor_year', 'source_age', 'genre_grouped']].copy()

    a_age_yr['year'] = a_age_yr['sailor_year'].astype(str)


    # 4. Individual references (for dot plot)

    a_dot_data = a_influence_edges[[

        'sailor_year', 'ref_name', 'ref_year', 'genre_grouped',

        'inf_type', 'source_age', 'sailor_work_name'

    ]].copy()

    a_dot_data['year'] = a_dot_data['sailor_year'].astype(str)
    return a_dot_data, a_genre_yr, a_type_yr


@app.cell
def _(a_dot_data, a_genre_yr, a_type_yr, alt):
    # ================================================================

    # CHART SET 1a

    #

    # Top-left  : Stacked bar — genre of sources by Sailor's work year

    # Top-right : Stacked bar — influence type by year

    # Bottom    : Dot plot — each reference as a point,

    #             x = Sailor's work year, y = source age,

    #             color = genre, shape = influence type

    #             → shows whether she digs deeper into the past over time

    # ================================================================


    # ── A. Genre × year stacked bar ─────────────────────────────────

    a_sel_genre = alt.selection_point(fields=['genre_grouped'], bind='legend')


    a_genre_bar = alt.Chart(a_genre_yr).mark_bar().encode(

        x=alt.X('year:O', title="Year of Sailor's Work",

                 axis=alt.Axis(labelAngle=-45)),

        y=alt.Y('count:Q', title='Influence References'),

        color=alt.Color('genre_grouped:N', title='Genre of Source',

                         scale=alt.Scale(scheme='tableau10')),

        opacity=alt.condition(a_sel_genre, alt.value(1), alt.value(0.15)),

        tooltip=[

            alt.Tooltip('year:O', title="Sailor's Year"),

            alt.Tooltip('genre_grouped:N', title='Source Genre'),

            alt.Tooltip('count:Q', title='References'),

        ]

    ).add_params(a_sel_genre).properties(

        title='Genre of Works Sailor Drew From, by Year',

        width=310, height=220

    )


    # ── B. Influence type × year stacked bar ────────────────────────

    a_type_colors = {

        'InStyleOf':          '#4c78a8',

        'CoverOf':            '#e07b39',

        'InterpolatesFrom':   '#54a24b',

        'LyricalReferenceTo': '#eeca3b',

        'DirectlySamples':    '#b279a2',

    }


    a_type_bar = alt.Chart(a_type_yr).mark_bar().encode(

        x=alt.X('year:O', title="Year of Sailor's Work",

                 axis=alt.Axis(labelAngle=-45)),

        y=alt.Y('count:Q', title=''),

        color=alt.Color(

            'inf_type:N', title='Influence Type',

            scale=alt.Scale(

                domain=list(a_type_colors.keys()),

                range=list(a_type_colors.values())

            )

        ),

        tooltip=[

            alt.Tooltip('year:O', title="Sailor's Year"),

            alt.Tooltip('inf_type:N', title='Type'),

            alt.Tooltip('count:Q', title='References'),

        ]

    ).properties(

        title='How Sailor Referenced Others (by type)',

        width=310, height=220

    )


    # ── C. Dot plot — each reference, source age vs year ────────────

    a_dot = alt.Chart(a_dot_data).mark_circle(size=90, opacity=0.8).encode(

        x=alt.X('year:O', title="Year of Sailor's Work",

                 axis=alt.Axis(labelAngle=-45)),

        y=alt.Y('source_age:Q',

                 title='Age of Referenced Work (years old when cited)'),

        color=alt.Color('genre_grouped:N', title='Source Genre',

                         scale=alt.Scale(scheme='tableau10')),

        shape=alt.Shape('inf_type:N', title='Influence Type'),

        tooltip=[

            alt.Tooltip('sailor_work_name:N', title="Sailor's Work"),

            alt.Tooltip('ref_name:N', title='Referenced Work'),

            alt.Tooltip('ref_year:Q', title='Source Released'),

            alt.Tooltip('source_age:Q', title='Years Old When Cited'),

            alt.Tooltip('genre_grouped:N', title='Genre'),

            alt.Tooltip('inf_type:N', title='Type'),

        ]

    ).properties(

        title='Each Influence Reference: How Old Was the Source When Sailor Drew On It?',

        width=640, height=260

    )


    alt.vconcat(

        alt.hconcat(a_genre_bar, a_type_bar).resolve_scale(color='independent'),

        a_dot

    ).resolve_scale(color='independent', shape='independent')
    return


@app.cell
def _():
    return


@app.cell
def _(a_dot_data, alt, mo):
    # ================================================================

    # Every source influenced Sailor exactly once.

    # Left : lollipop — all dots at x=1, sorted by source age,

    #        colored by genre, shaped by influence type.

    # Right: plain marimo table — the full reference list.

    # ================================================================


    a_ref_table = (

        a_dot_data[[

            'ref_name', 'genre_grouped', 'inf_type',

            'ref_year', 'source_age', 'sailor_work_name', 'year'

        ]]

        .drop_duplicates(subset=['ref_name'])

        .sort_values('source_age', ascending=False)

        .reset_index(drop=True)

    )

    a_ref_table['count'] = 1

    a_ref_table['ref_label'] = (

        a_ref_table['ref_name'].str[:32]

        + '  (' + a_ref_table['genre_grouped'] + ')'

    )


    # ── Lollipop ─────────────────────────────────────────────────────

    a_stem = alt.Chart(a_ref_table).mark_rule(

        color='#cccccc', strokeWidth=1.5

    ).encode(

        y=alt.Y('ref_label:N',

                 sort=alt.EncodingSortField('source_age', order='descending'),

                 title='Referenced Work (genre)',

                 axis=alt.Axis(labelLimit=280, labelFontSize=10)),

        x=alt.X('count:Q',

                 scale=alt.Scale(domain=[0, 1.5]),

                 title='Times Cited by Sailor',

                 axis=alt.Axis(tickCount=2, values=[0, 1])),

    )


    a_head = alt.Chart(a_ref_table).mark_circle(opacity=0.9).encode(

        y=alt.Y('ref_label:N',

                 sort=alt.EncodingSortField('source_age', order='descending')),

        x=alt.X('count:Q', scale=alt.Scale(domain=[0, 1.5])),

        color=alt.Color('genre_grouped:N', title='Genre',

                         scale=alt.Scale(scheme='tableau10')),

        size=alt.Size('source_age:Q', title='Age of Source (yrs)',

                       scale=alt.Scale(range=[60, 400])),

        shape=alt.Shape('inf_type:N', title='Influence Type'),

        tooltip=[

            alt.Tooltip('ref_name:N',        title='Referenced Work'),

            alt.Tooltip('genre_grouped:N',   title='Genre'),

            alt.Tooltip('inf_type:N',        title='Influence Type'),

            alt.Tooltip('ref_year:Q',        title='Source Released'),

            alt.Tooltip('source_age:Q',      title='Years Old When Cited'),

            alt.Tooltip('sailor_work_name:N',title="Sailor's Work"),

            alt.Tooltip('year:O',            title="Sailor's Year"),

        ]

    )


    a_lollipop = (a_stem + a_head).properties(

        title='Every Work That Influenced Sailor — Each Cited Exactly Once',

        width=360, height=660

    )


    # ── Table ─────────────────────────────────────────────────────────

    a_display_table = (

        a_ref_table[[

            'ref_name', 'genre_grouped', 'inf_type',

            'ref_year', 'source_age', 'sailor_work_name', 'year', 'count'

        ]]

        .rename(columns={

            'ref_name':          'Referenced Work',

            'genre_grouped':     'Genre',

            'inf_type':          'Influence Type',

            'ref_year':          'Src Year',

            'source_age':        'Age (yrs)',

            'sailor_work_name':  "Sailor's Work",

            'year':              "Sailor's Year",

            'count':             'Times Cited',

        })

    )


    mo.hstack([

        a_lollipop,

        mo.ui.table(a_display_table, selection=None)

    ], gap=2)
    return


@app.cell
def _():
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Task 1b — Who has Sailor Shift collaborated with and directly or indirectly influenced?
    """)
    return


@app.cell
def _():
    return


@app.cell
def _(edges_df, nodes_df, pd, sailor_id):
    b_collab_types    = ['PerformerOf', 'ComposerOf', 'ProducerOf', 'LyricistOf']

    b_influence_types = ['InStyleOf', 'CoverOf', 'DirectlySamples',

                         'InterpolatesFrom', 'LyricalReferenceTo']


    b_person_ids = set(nodes_df[nodes_df['node_type'] == 'Person']['node_id'])

    b_artist_names = nodes_df[['node_id', 'name']].rename(

        columns={'node_id': 'artist_id', 'name': 'artist_name'}

    )


    # ------------------------------------------------------------------

    # Confirmed edge semantics (from Task 2):

    #   source  →  target

    #   "source influences target" / "source is InStyleOf target"

    #   So "works influenced BY Sailor" = source ∈ sailor_work_ids

    # ------------------------------------------------------------------


    # A. Sailor's own works  (PerformerOf: source=Sailor → target=work)

    b_sailor_work_ids = set(

        edges_df[

            (edges_df['source'] == sailor_id) &

            (edges_df['edge_type'].isin(b_collab_types))

        ]['target']

    )

    print(f"Sailor works found: {len(b_sailor_work_ids)}")


    # ------------------------------------------------------------------

    # B. Collaborators — other people whose PerformerOf target

    #    overlaps with Sailor's works

    # ------------------------------------------------------------------

    b_co_edges = edges_df[

        (edges_df['target'].isin(b_sailor_work_ids)) &

        (edges_df['edge_type'].isin(b_collab_types)) &

        (edges_df['source'] != sailor_id)

    ][['source', 'target', 'edge_type']].rename(

        columns={'source': 'person_id', 'target': 'work_id', 'edge_type': 'role'}

    )

    b_co_edges = b_co_edges[b_co_edges['person_id'].isin(b_person_ids)]

    b_co_edges = b_co_edges.merge(

        nodes_df[['node_id', 'name']].rename(

            columns={'node_id': 'person_id', 'name': 'collab_name'}),

        on='person_id', how='left'

    )

    b_co_edges = b_co_edges.merge(

        nodes_df[['node_id', 'release_year', 'name']].rename(

            columns={'node_id': 'work_id', 'name': 'work_name'}),

        on='work_id', how='left'

    )

    b_co_edges = b_co_edges.dropna(subset=['release_year'])

    b_co_edges['year'] = b_co_edges['release_year'].astype(int)


    b_collab_summary = (

        b_co_edges.groupby(['person_id', 'collab_name'])

        .agg(

            collaborations=('work_id', 'nunique'),

            first_year=('year', 'min'),

            last_year=('year', 'max'),

            roles=('role', lambda x: ', '.join(sorted(set(x))))

        )

        .reset_index()

        .sort_values('collaborations', ascending=False)

    )


    # ------------------------------------------------------------------

    # C. Direct influence

    #    "source influences target" → Sailor's work is the SOURCE,

    #    the influenced work is the TARGET.

    #    Filter: source ∈ sailor_work_ids

    # ------------------------------------------------------------------

    b_direct_inf_edges = edges_df[

        (edges_df['source'].isin(b_sailor_work_ids)) &

        (edges_df['edge_type'].isin(b_influence_types))

    ][['source', 'target', 'edge_type']].rename(

        columns={'source': 'sailor_work_id',

                 'target': 'influenced_work_id',

                 'edge_type': 'inf_type'}

    )

    print(f"Direct influence edges found: {len(b_direct_inf_edges)}")


    # Resolve influenced works → performing artists

    # PerformerOf: source=Person → target=Work

    b_influenced_work_ids = set(b_direct_inf_edges['influenced_work_id'])

    b_direct_performers = edges_df[

        (edges_df['target'].isin(b_influenced_work_ids)) &

        (edges_df['edge_type'] == 'PerformerOf')

    ][['source', 'target']].rename(

        columns={'source': 'artist_id', 'target': 'influenced_work_id'}

    )

    b_direct_performers = b_direct_performers[

        b_direct_performers['artist_id'].isin(b_person_ids)

    ]


    b_direct_inf = b_direct_inf_edges.merge(

        b_direct_performers, on='influenced_work_id', how='left'

    )

    b_direct_inf = b_direct_inf.merge(

        nodes_df[['node_id', 'release_year', 'genre']].rename(

            columns={'node_id': 'influenced_work_id'}),

        on='influenced_work_id', how='left'

    )

    b_direct_inf = b_direct_inf.dropna(subset=['release_year', 'artist_id'])

    b_direct_inf['year'] = b_direct_inf['release_year'].astype(int)


    b_direct_summary = (

        b_direct_inf.merge(b_artist_names, on='artist_id', how='left')

        .groupby(['artist_id', 'artist_name', 'genre'])

        .agg(refs=('influenced_work_id', 'nunique'))

        .reset_index()

        .sort_values('refs', ascending=False)

    )

    b_direct_summary = b_direct_summary[b_direct_summary['artist_id'] != sailor_id]


    # ------------------------------------------------------------------

    # D. Indirect influence (2-hop)

    #    Works directly influenced by Sailor → those works influence others

    #    source ∈ b_directly_influenced_ids

    # ------------------------------------------------------------------

    b_directly_influenced_ids = set(b_direct_inf_edges['influenced_work_id'])


    b_indirect_inf_edges = edges_df[

        (edges_df['source'].isin(b_directly_influenced_ids)) &

        (edges_df['edge_type'].isin(b_influence_types))

    ][['source', 'target']].rename(

        columns={'source': 'direct_work_id', 'target': 'indirect_work_id'}

    )

    print(f"Indirect influence edges found: {len(b_indirect_inf_edges)}")


    b_indirect_work_ids = set(b_indirect_inf_edges['indirect_work_id'])

    b_indirect_performers = edges_df[

        (edges_df['target'].isin(b_indirect_work_ids)) &

        (edges_df['edge_type'] == 'PerformerOf')

    ][['source', 'target']].rename(

        columns={'source': 'artist_id', 'target': 'indirect_work_id'}

    )

    b_indirect_performers = b_indirect_performers[

        b_indirect_performers['artist_id'].isin(b_person_ids)

    ]


    b_indirect_inf = b_indirect_inf_edges.merge(

        b_indirect_performers, on='indirect_work_id', how='left'

    ).dropna(subset=['artist_id'])

    b_indirect_inf = b_indirect_inf.merge(

        nodes_df[['node_id', 'release_year', 'genre']].rename(

            columns={'node_id': 'indirect_work_id'}),

        on='indirect_work_id', how='left'

    ).dropna(subset=['release_year'])

    b_indirect_inf['year'] = b_indirect_inf['release_year'].astype(int)


    b_indirect_summary = (

        b_indirect_inf.merge(b_artist_names, on='artist_id', how='left')

        .groupby(['artist_id', 'artist_name', 'genre'])

        .agg(refs=('indirect_work_id', 'nunique'))

        .reset_index()

        .sort_values('refs', ascending=False)

    )

    b_direct_artist_ids = set(b_direct_summary['artist_id'])

    b_indirect_summary = b_indirect_summary[

        ~b_indirect_summary['artist_id'].isin(b_direct_artist_ids | {sailor_id})

    ]


    # ------------------------------------------------------------------

    # E. Combined

    # ------------------------------------------------------------------

    b_direct_summary['influence_type']   = 'Direct'

    b_indirect_summary['influence_type'] = 'Indirect'


    b_influenced_combined = pd.concat(

        [b_direct_summary, b_indirect_summary], ignore_index=True

    )


    print(f"Collaborators        : {len(b_collab_summary)}")

    print(f"Directly influenced  : {len(b_direct_summary)}")

    print(f"Indirectly influenced: {len(b_indirect_summary)}")

    print(f"Combined rows        : {len(b_influenced_combined)}")
    return b_co_edges, b_collab_summary, b_influenced_combined


@app.cell
def _():
    return


@app.cell
def _(alt, b_co_edges, b_collab_summary):
    TOP_COLLABS = 15

    b_top_collabs = b_collab_summary.head(TOP_COLLABS).copy()


    # ── Bar chart (unchanged) ────────────────────────────────────────

    b_collab_bar = alt.Chart(b_top_collabs).mark_bar().encode(

        x=alt.X('collaborations:Q', title='Shared Works'),

        y=alt.Y('collab_name:N', sort='-x', title='Collaborator'),

        color=alt.Color('roles:N', title='Role(s)',

                         scale=alt.Scale(scheme='set2')),

        tooltip=[

            alt.Tooltip('collab_name:N', title='Artist'),

            alt.Tooltip('collaborations:Q', title='Shared Works'),

            alt.Tooltip('roles:N', title='Role(s)'),

            alt.Tooltip('first_year:Q', title='First Year'),

            alt.Tooltip('last_year:Q', title='Last Year'),

        ]

    ).properties(

        title=f'Top {TOP_COLLABS} Collaborators of Sailor Shift',

        width=380, height=340

    )


    # ── Dot strip plot — one dot per collaboration year ──────────────

    # Each row is already one work per year, so just plot a uniform dot

    b_collab_filtered = b_co_edges[

        b_co_edges['collab_name'].isin(b_top_collabs['collab_name'])

    ].drop_duplicates(subset=['collab_name', 'year'])


    b_dot_strip = alt.Chart(b_collab_filtered).mark_circle(

        size=120, opacity=0.85, color='#4c78a8'

    ).encode(

        x=alt.X('year:O', title='Year', axis=alt.Axis(labelAngle=-45)),

        y=alt.Y('collab_name:N', title='Collaborator',

                 sort=alt.SortField('collaborations', order='descending')),

        tooltip=[

            alt.Tooltip('year:O', title='Year'),

            alt.Tooltip('collab_name:N', title='Collaborator'),

            alt.Tooltip('work_name:N', title='Work'),

            alt.Tooltip('role:N', title='Role'),

        ]

    ).properties(

        title='When Did Sailor Collaborate? (one dot = one shared work)',

        width=380, height=340

    )


    alt.hconcat(

        b_collab_bar,

        b_dot_strip

    ).resolve_scale(color='independent')
    return


@app.cell
def _():
    return


@app.cell
def _(alt, b_influenced_combined, mo):
    TOP_INF = 12


    b_top_inf_artists = (

        b_influenced_combined.groupby('artist_name')['refs']

        .sum()

        .nlargest(TOP_INF)

        .index

        .tolist()

    )


    b_inf_bar_data = (

        b_influenced_combined[b_influenced_combined['artist_name'].isin(b_top_inf_artists)]

        .groupby(['artist_name', 'influence_type'])['refs']

        .sum()

        .reset_index()

    )


    # ── Bar chart ────────────────────────────────────────────────────

    b_inf_bar = alt.Chart(b_inf_bar_data).mark_bar().encode(

        x=alt.X('refs:Q', title='Works Referencing Sailor',

                 axis=alt.Axis(tickMinStep=1)),

        y=alt.Y('artist_name:N', sort='-x', title='Artist'),

        color=alt.Color(

            'influence_type:N',

            title='Influence Depth',

            scale=alt.Scale(

                domain=['Direct', 'Indirect'],

                range=['#e07b39', '#aec7e8']

            ),

            legend=alt.Legend(title='Influence Depth')

        ),

        xOffset='influence_type:N',

        tooltip=[

            alt.Tooltip('artist_name:N', title='Artist'),

            alt.Tooltip('influence_type:N', title='Direct / Indirect'),

            alt.Tooltip('refs:Q', title='Works'),

        ]

    ).properties(

        title=f'Top {TOP_INF} Artists Influenced by Sailor Shift',

        width=500, height=340

    )


    # ── Genre summary table ──────────────────────────────────────────

    b_genre_summary = (

        b_influenced_combined

        .groupby(['genre', 'influence_type'])['refs']

        .sum()

        .reset_index()

        .pivot_table(index='genre', columns='influence_type', values='refs', fill_value=0)

        .reset_index()

    )

    b_genre_summary.columns.name = None


    # Ensure both columns exist even if one influence type is absent

    for _col in ['Direct', 'Indirect']:

        if _col not in b_genre_summary.columns:

            b_genre_summary[_col] = 0


    b_genre_summary['Total'] = b_genre_summary['Direct'] + b_genre_summary['Indirect']

    b_genre_summary = b_genre_summary.sort_values('Total', ascending=False)

    b_genre_summary = b_genre_summary.rename(columns={'genre': 'Genre'})


    mo.hstack([

        b_inf_bar,

        mo.vstack([

            mo.md("**Genre breakdown of influenced artists**"),

            mo.ui.table(b_genre_summary, selection=None)

        ])

    ], gap=2)
    return


@app.cell
def _(alt, b_influenced_combined, mo):
    # ================================================================

    # CHART SET 3  —  Genre reach: direct vs indirect

    # ================================================================

    b_top_genres2 = (

        b_influenced_combined.groupby('genre')['refs']

        .sum()

        .nlargest(7)

        .index.tolist()

    )

    b_influenced_combined['genre_grouped2'] = b_influenced_combined['genre'].apply(

        lambda x: x if x in b_top_genres2 else 'Other'

    )


    b_genre_inf_type = (

        b_influenced_combined

        .groupby(['genre_grouped2', 'influence_type'])['refs']

        .sum()

        .reset_index()

    )


    b_stacked_reach = alt.Chart(b_genre_inf_type).mark_bar().encode(

        x=alt.X('refs:Q', title='Number of Artists Reached'),

        y=alt.Y('genre_grouped2:N', sort='-x', title='Genre'),

        color=alt.Color(

            'influence_type:N',

            title='Influence Depth',

            scale=alt.Scale(

                domain=['Direct', 'Indirect'],

                range=['#e07b39', '#aec7e8']

            )

        ),

        tooltip=[

            alt.Tooltip('genre_grouped2:N', title='Genre'),

            alt.Tooltip('influence_type:N', title='Depth'),

            alt.Tooltip('refs:Q', title='Artists Reached'),

        ]

    ).properties(

        title="Sailor Shift's Influence Reach by Genre (Direct vs Indirect)",

        width=580, height=320

    )


    mo.ui.altair_chart(b_stacked_reach)
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Task 1c — How has Sailor Shift influenced collaborators and the broader Oceanus Folk community?
    """)
    return


@app.cell
def _():
    return


@app.cell
def _(edges_df, nodes_df, sailor_id):
    c_collab_types = ['PerformerOf', 'ComposerOf', 'ProducerOf', 'LyricistOf']

    BREAKTHROUGH = 2028


    c_sailor_work_ids = set(edges_df[

        (edges_df['source'] == sailor_id) &

        (edges_df['edge_type'].isin(c_collab_types))

    ]['target'])


    c_collab_ids = set(edges_df[

        (edges_df['target'].isin(c_sailor_work_ids)) &

        (edges_df['edge_type'].isin(c_collab_types)) &

        (edges_df['source'] != sailor_id)

    ]['source'])


    # First collab year per collaborator

    c_first_collab = (

        edges_df[

            (edges_df['target'].isin(c_sailor_work_ids)) &

            (edges_df['edge_type'].isin(c_collab_types)) &

            (edges_df['source'].isin(c_collab_ids))

        ]

        .merge(

            nodes_df[['node_id', 'release_year']].rename(

                columns={'node_id': 'target'}),

            on='target', how='left'

        )

        .dropna(subset=['release_year'])

        .groupby('source')['release_year']

        .min()

        .reset_index()

        .rename(columns={'source': 'person_id',

                         'release_year': 'first_collab_year'})

    )

    c_first_collab['first_collab_year'] = c_first_collab['first_collab_year'].astype(int)


    # Deduplicated works

    c_collab_work_ids = set(edges_df[

        (edges_df['source'].isin(c_collab_ids)) &

        (edges_df['edge_type'].isin(c_collab_types))

    ]['target'])


    c_works_deduped = (

        nodes_df[nodes_df['node_id'].isin(c_collab_work_ids)]

        [['node_id', 'genre', 'release_year', 'notable']]

        .drop_duplicates(subset=['node_id'])

        .rename(columns={'node_id': 'work_id'})

        .dropna(subset=['release_year'])

        .copy()

    )

    c_works_deduped['year'] = c_works_deduped['release_year'].astype(int)

    c_works_deduped = c_works_deduped[c_works_deduped['year'] > 0]

    c_works_deduped['notable'] = c_works_deduped['notable'].astype(bool)


    # Work → person mapping

    c_work_to_person = edges_df[

        (edges_df['source'].isin(c_collab_ids)) &

        (edges_df['edge_type'].isin(c_collab_types)) &

        (edges_df['target'].isin(c_works_deduped['work_id']))

    ][['source', 'target']].rename(

        columns={'source': 'person_id', 'target': 'work_id'}

    ).drop_duplicates()


    # Minimum first_collab_year per work

    c_work_period = (

        c_work_to_person.merge(c_first_collab, on='person_id', how='left')

        .groupby('work_id')['first_collab_year']

        .min()

        .reset_index()

    )


    # Yearly notable rate (work-level, deduplicated)

    c_collab_works = c_works_deduped.merge(

        c_work_period, on='work_id', how='left'

    ).dropna(subset=['first_collab_year'])

    c_collab_works['first_collab_year'] = c_collab_works['first_collab_year'].astype(int)

    c_collab_works['period'] = c_collab_works.apply(

        lambda r: 'After collab' if r['year'] >= r['first_collab_year']

                  else 'Before collab', axis=1

    )


    c_notability_yr = (

        c_collab_works.groupby(['year', 'period'])

        .agg(

            total_works=('work_id', 'nunique'),

            notable_works=('notable', 'sum')

        )

        .reset_index()

    )

    c_notability_yr['notable_rate'] = (

        c_notability_yr['notable_works'] / c_notability_yr['total_works']

    ).clip(upper=1.0)


    # Per-person notable rate before vs after

    # Fix: merge c_first_collab BEFORE dropna so the column exists

    c_per_person = (

        c_work_to_person

        .merge(c_works_deduped[['work_id', 'year', 'notable']], on='work_id')

        .merge(c_first_collab, on='person_id', how='left')   # ← must be before dropna

        .dropna(subset=['first_collab_year'])

    )

    c_per_person['first_collab_year'] = c_per_person['first_collab_year'].astype(int)

    c_per_person['period'] = c_per_person.apply(

        lambda r: 'After collab' if r['year'] >= r['first_collab_year']

                  else 'Before collab', axis=1

    )

    c_per_person['notable'] = c_per_person['notable'].astype(bool)


    c_per_person_agg = (

        c_per_person.groupby(['person_id', 'period'])

        .agg(total=('work_id', 'nunique'), notable=('notable', 'sum'))

        .reset_index()

    )

    c_per_person_agg['notable_rate'] = (

        c_per_person_agg['notable'] / c_per_person_agg['total']

    ).clip(upper=1.0)


    c_per_person_agg = c_per_person_agg.merge(

        nodes_df[['node_id', 'name']].rename(

            columns={'node_id': 'person_id', 'name': 'collab_name'}),

        on='person_id', how='left'

    )


    c_both = c_per_person_agg.groupby('person_id')['period'].nunique()

    c_pivot_notability = (

        c_per_person_agg[

            c_per_person_agg['person_id'].isin(c_both[c_both == 2].index)

        ]

        .pivot_table(index=['person_id', 'collab_name'],

                     columns='period', values='notable_rate')

        .reset_index()

    )

    c_pivot_notability.columns.name = None

    c_pivot_notability = c_pivot_notability.rename(columns={

        'Before collab': 'before', 'After collab': 'after'

    }).fillna(0)

    c_pivot_notability['delta'] = c_pivot_notability['after'] - c_pivot_notability['before']

    c_pivot_notability = c_pivot_notability.sort_values('delta', ascending=False)


    print(f"Collaborators with pre+post data: {len(c_pivot_notability)}")

    print(f"Max notable rate: {c_per_person_agg['notable_rate'].max():.2f}")
    return c_notability_yr, c_pivot_notability


@app.cell
def _(alt, c_notability_yr, c_pivot_notability):
    # ================================================================

    # CHART 1 — Collaborator notability before vs after working with Sailor

    # Rendered directly (not via mo.ui.altair_chart) to avoid marimo

    # injecting a duplicate pan_zoom_year signal into combined charts.

    # ================================================================


    c_notability_line = alt.Chart(c_notability_yr).mark_line(point=True).encode(

        x=alt.X('year:O', title='Year', axis=alt.Axis(labelAngle=-45)),

        y=alt.Y('notable_rate:Q', title='Share of Notable Works',

                 axis=alt.Axis(format='%')),

        color=alt.Color(

            'period:N', title='Period',

            scale=alt.Scale(

                domain=['Before collab', 'After collab'],

                range=['#aec7e8', '#e07b39']

            )

        ),

        tooltip=[

            alt.Tooltip('year:O', title='Year'),

            alt.Tooltip('period:N', title='Period'),

            alt.Tooltip('notable_rate:Q', title='Notable Rate', format='.0%'),

            alt.Tooltip('total_works:Q', title='Total Works'),

        ]

    ).properties(

        title="Sailor's Collaborators: Share of Notable Works Before vs After Collaborating",

        width=620, height=240

    )


    c_delta_bar = alt.Chart(c_pivot_notability.head(15)).mark_bar().encode(

        x=alt.X('delta:Q', title='Δ Notable Rate (After − Before)',

                 axis=alt.Axis(format='%')),

        y=alt.Y('collab_name:N', sort='-x', title='Collaborator'),

        color=alt.condition(

            alt.datum.delta > 0,

            alt.value('#2ca02c'),

            alt.value('#d62728')

        ),

        tooltip=[

            alt.Tooltip('collab_name:N', title='Collaborator'),

            alt.Tooltip('delta:Q', title='Δ Notable Rate', format='.0%'),

            alt.Tooltip('before:Q', title='Before', format='.0%'),

            alt.Tooltip('after:Q', title='After', format='.0%'),

        ]

    ).properties(

        title='Change in Notable Work Rate After First Collaborating with Sailor',

        width=620, height=300

    )


    alt.vconcat(

        c_notability_line,

        c_delta_bar

    ).resolve_scale(color='independent')
    return


@app.cell
def _():
    return


@app.cell
def _(edges_df, nodes_df, of_ids, sailor_id):
    c2_collab_types    = ['PerformerOf', 'ComposerOf', 'ProducerOf', 'LyricistOf']

    c2_influence_types = ['InStyleOf', 'CoverOf', 'DirectlySamples',

                          'InterpolatesFrom', 'LyricalReferenceTo']

    BREAKTHROUGH_YR = 2028

    c2_of_set = set(of_ids)


    c2_sailor_work_ids = set(edges_df[

        (edges_df['source'] == sailor_id) &

        (edges_df['edge_type'].isin(c2_collab_types))

    ]['target'])


    c2_collab_ids = set(edges_df[

        (edges_df['target'].isin(c2_sailor_work_ids)) &

        (edges_df['edge_type'].isin(c2_collab_types)) &

        (edges_df['source'] != sailor_id)

    ]['source'])


    c2_collab_work_ids = set(edges_df[

        (edges_df['source'].isin(c2_collab_ids)) &

        (edges_df['edge_type'].isin(c2_collab_types))

    ]['target'])


    # ------------------------------------------------------------------

    # OF internal influence network

    # ------------------------------------------------------------------

    c2_of_to_of = edges_df[

        (edges_df['source'].isin(c2_of_set)) &

        (edges_df['target'].isin(c2_of_set)) &

        (edges_df['edge_type'].isin(c2_influence_types))

    ][['source', 'target', 'edge_type']]


    # In-degree: how many OF works cite each OF work

    c2_of_indegree = (

        c2_of_to_of.groupby('target').size()

        .reset_index(name='of_citations')

        .rename(columns={'target': 'work_id'})

    )

    c2_of_indegree = c2_of_indegree.merge(

        nodes_df[['node_id', 'name', 'release_year', 'notable']].rename(

            columns={'node_id': 'work_id'}),

        on='work_id', how='left'

    ).dropna(subset=['release_year'])

    c2_of_indegree['year'] = c2_of_indegree['release_year'].astype(int)

    c2_of_indegree = c2_of_indegree[c2_of_indegree['year'] > 0]

    c2_of_indegree['by_collab'] = c2_of_indegree['work_id'].isin(c2_collab_work_ids)


    c_top_of_cited = c2_of_indegree.nlargest(20, 'of_citations')


    # OF internal citations per year

    c2_of_citations_yr = (

        c2_of_to_of.merge(

            nodes_df[['node_id', 'release_year']].rename(

                columns={'node_id': 'source'}),

            on='source', how='left'

        ).dropna(subset=['release_year'])

    )

    c2_of_citations_yr['year'] = c2_of_citations_yr['release_year'].astype(int)

    c2_of_citations_yr = c2_of_citations_yr[c2_of_citations_yr['year'] > 0]

    c2_of_citations_yr['era'] = c2_of_citations_yr['year'].apply(

        lambda y: f'After {BREAKTHROUGH_YR}' if y >= BREAKTHROUGH_YR

                  else f'Before {BREAKTHROUGH_YR}'

    )

    c_of_network_by_year = (

        c2_of_citations_yr.groupby(['year', 'era'])['source']

        .nunique()

        .reset_index(name='of_works_citing_of')

    )


    # ------------------------------------------------------------------

    # Genre palette: Sailor vs OF community

    # ------------------------------------------------------------------

    c_sailor_cited_genres = (

        edges_df[

            (edges_df['source'].isin(c2_sailor_work_ids)) &

            (edges_df['edge_type'].isin(c2_influence_types))

        ]

        .merge(

            nodes_df[['node_id', 'genre']].rename(columns={'node_id': 'target'}),

            on='target', how='left'

        )

        .groupby('genre').size()

        .reset_index(name='sailor_citations')

        .sort_values('sailor_citations', ascending=False)

    )

    c_sailor_cited_genres = c_sailor_cited_genres[

        c_sailor_cited_genres['genre'] != 'Oceanus Folk'

    ]


    c2_of_cited_genres = (

        edges_df[

            (edges_df['source'].isin(c2_of_set)) &

            (~edges_df['target'].isin(c2_of_set)) &

            (edges_df['edge_type'].isin(c2_influence_types))

        ]

        .merge(

            nodes_df[['node_id', 'genre']].rename(columns={'node_id': 'target'}),

            on='target', how='left'

        )

        .groupby('genre').size()

        .reset_index(name='of_citations')

        .sort_values('of_citations', ascending=False)

    )

    c2_of_cited_genres = c2_of_cited_genres[

        ~c2_of_cited_genres['genre'].isin(['Oceanus Folk', 'Unknown'])

    ]


    c_genre_compare = c2_of_cited_genres.merge(

        c_sailor_cited_genres, on='genre', how='outer'

    ).fillna(0)

    c_genre_compare['of_share'] = (

        c_genre_compare['of_citations'] / c_genre_compare['of_citations'].sum()

    )

    c_genre_compare['sailor_share'] = (

        c_genre_compare['sailor_citations'] / c_genre_compare['sailor_citations'].sum()

    )

    c_genre_compare = c_genre_compare.sort_values('of_citations', ascending=False)


    print(f"Top cited OF work: {c_top_of_cited.iloc[0]['name']} "

          f"({int(c_top_of_cited.iloc[0]['of_citations'])} citations)")

    print(f"OF internal edges: {len(c2_of_to_of)}")
    return c_genre_compare, c_sailor_cited_genres


@app.cell
def _():
    return


@app.cell
def _(alt, c_genre_compare, c_sailor_cited_genres, mo):
    # ================================================================

    # CHART 3 — Genre palette: Sailor vs broader OF community

    # ================================================================

    import pandas as _pd


    TOP_GENRES = 12

    c_top_genre_names = c_genre_compare.head(TOP_GENRES)['genre'].tolist()

    c_gc_top = c_genre_compare[c_genre_compare['genre'].isin(c_top_genre_names)].copy()


    # Reshape to long for grouped bar

    c_gc_long = _pd.melt(

        c_gc_top,

        id_vars=['genre'],

        value_vars=['of_share', 'sailor_share'],

        var_name='source',

        value_name='share'

    )

    c_gc_long['source'] = c_gc_long['source'].map({

        'of_share':     'OF Community',

        'sailor_share': 'Sailor Shift'

    })


    c_palette_bar = alt.Chart(c_gc_long).mark_bar().encode(

        x=alt.X('share:Q', title='Share of External Citations',

                 axis=alt.Axis(format='%')),

        y=alt.Y('genre:N', sort='-x', title='Genre'),

        color=alt.Color(

            'source:N', title='Who is citing?',

            scale=alt.Scale(

                domain=['OF Community', 'Sailor Shift'],

                range=['#4c78a8', '#e07b39']

            )

        ),

        xOffset='source:N',

        tooltip=[

            alt.Tooltip('genre:N', title='Genre'),

            alt.Tooltip('source:N', title='Source'),

            alt.Tooltip('share:Q', title='Share', format='.1%'),

        ]

    ).properties(

        title='External Genre Influences: Sailor Shift vs the Broader OF Community',

        width=500, height=340

    )


    # Sailor's absolute citations as small annotation bar

    c_sailor_abs = alt.Chart(

        c_sailor_cited_genres[c_sailor_cited_genres['genre'].isin(c_top_genre_names)]

    ).mark_bar(color='#e07b39', opacity=0.7).encode(

        x=alt.X('sailor_citations:Q', title='Sailor: Raw Citation Count'),

        y=alt.Y('genre:N', sort='-x', title=''),

        tooltip=[

            alt.Tooltip('genre:N', title='Genre'),

            alt.Tooltip('sailor_citations:Q', title='Sailor Citations'),

        ]

    ).properties(

        title="Sailor's Raw Citation Counts by Genre",

        width=200, height=340

    )


    mo.ui.altair_chart(c_palette_bar | c_sailor_abs)
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
