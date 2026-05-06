import marimo

__generated_with = "0.19.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import networkx as nx
    import json
    import pandas as pd
    import altair as alt
    from sklearn.preprocessing import StandardScaler
    import numpy as np

    #can adjust according to your own path
    file_path = "MC1-data/MC1_graph.json"


    #load data
    with open(file_path, 'r') as f:
        data = json.load(f)

    G = nx.node_link_graph(data, edges='links')

    print(f"Nodes: {G.number_of_nodes():,}")
    print(f"Edges: {G.number_of_edges():,}")


    #node data to DataFrame
    nodes_data = []
    for node_id, attrs in G.nodes(data=True):
        nodes_data.append({'node_id': node_id, **attrs})
    nodes_df = pd.DataFrame(nodes_data)

    print("\nDataFrame columns:", nodes_df.columns.tolist())

    #edges_data to dataframe
    edges_data = []
    for u, v, attrs in G.edges(data=True):
        edges_data.append({
            'source': u, 
            'target': v,
            **attrs
        })
    edges_df = pd.DataFrame(edges_data)

    print(f"edge shape: {edges_df.shape}")
    print(f"columns: {edges_df.columns.tolist()}")
    print(f"\n{edges_df['Edge Type'].value_counts()}")

    #Check sailor shift
    sailor = nodes_df[nodes_df['name'] == 'Sailor Shift']
    if len(sailor) > 0:
        print(sailor[['node_id', 'name', 'Node Type']])
        sailor_id = sailor.iloc[0]['node_id']

        # 查看Sailor的连接
        sailor_edges = edges_df[(edges_df['source'] == sailor_id) | (edges_df['target'] == sailor_id)]
        print(f"\nSailor connections: {len(sailor_edges)}")
        print(f"Connection types:\n{sailor_edges['Edge Type'].value_counts()}")
    else:
        print("Sailor Shift Not Found")
        persons = nodes_df[nodes_df['Node Type'] == 'Person']
        print(f"\nPerson(top5):")
        print(persons[['name']].head())
    return G, StandardScaler, alt, edges_df, mo, nodes_df, np, pd, sailor_id


@app.cell
def _(G, StandardScaler, edges_df, nodes_df, np, pd, sailor_id):
    pd.set_option('future.no_silent_downcasting', True) 

    # 1. 统一列名（转小写，方便后续处理）
    nodes_df.columns = [c.lower().replace(' ', '_') for c in nodes_df.columns]
    edges_df.columns = [c.lower().replace(' ', '_') for c in edges_df.columns]

    print("\n1. Column name adjusted:")
    print(f"nodes columns: {nodes_df.columns.tolist()}")
    print(f"edges columns: {edges_df.columns.tolist()}")

    # 2. 处理时间字段
    print("\n2. Dealing time columns")
    nodes_df['release_year'] = pd.to_numeric(nodes_df['release_date'], errors='coerce')
    nodes_df['notoriety_year'] = pd.to_numeric(nodes_df['notoriety_date'], errors='coerce')
    nodes_df['written_year'] = pd.to_numeric(nodes_df['written_date'], errors='coerce')
    print(f"Years range: {nodes_df['release_year'].min():.0f} - {nodes_df['release_year'].max():.0f}")

    # 3. 处理布尔值
    print("\n3. Dealing boolean")
    nodes_df['notable'] = nodes_df['notable'].fillna(False).astype(bool)
    nodes_df['single'] = nodes_df['single'].fillna(False).astype(bool)
    print(f" notables: {nodes_df['notable'].sum()}")
    print(f" singles: {nodes_df['single'].sum()}")

    # 4. 处理分类变量
    print("\n4. Dealing categories")
    nodes_df['genre'] = nodes_df['genre'].fillna('Unknown')
    nodes_df['stage_name'] = nodes_df['stage_name'].fillna('')
    nodes_df['name'] = nodes_df['name'].fillna('Unknown')

    # 5. 计算网络指标
    print("\n5. Calculating degree")
    degree_dict = dict(G.degree())
    nodes_df['degree'] = nodes_df['node_id'].map(degree_dict)

    # 计算每种边类型的度数
    for edge_type in edges_df['edge_type'].unique():
        source_counts = edges_df[edges_df['edge_type'] == edge_type].groupby('source').size()
        nodes_df[f'source_{edge_type.lower()}_count'] = nodes_df['node_id'].map(source_counts).fillna(0)

        target_counts = edges_df[edges_df['edge_type'] == edge_type].groupby('target').size()
        nodes_df[f'target_{edge_type.lower()}_count'] = nodes_df['node_id'].map(target_counts).fillna(0)

    print(f"degree range: {nodes_df['degree'].min()} - {nodes_df['degree'].max()}")

    # 6. 计算合作次数和影响力指标
    print("\n6. Calculating for artists")

    # 合作次数（所有节点都计算）
    collab_types = ['performerof', 'composerof', 'producerof', 'lyricistof']
    nodes_df['collaboration_count'] = 0

    for ctype in collab_types:
        source_col = f'source_{ctype}_count'
        target_col = f'target_{ctype}_count'

        if source_col in nodes_df.columns:
            nodes_df['collaboration_count'] += nodes_df[source_col]
        if target_col in nodes_df.columns:
            nodes_df['collaboration_count'] += nodes_df[target_col]

    # 影响力指标
    influence_types = {
        'influence_out': ['source_instyleof_count', 'source_lyricalreferenceto_count', 
                          'source_interpolatesfrom_count', 'source_coverof_count', 
                          'source_directlysamples_count'],
        'influence_in': ['target_instyleof_count', 'target_lyricalreferenceto_count',
                         'target_interpolatesfrom_count', 'target_coverof_count',
                         'target_directlysamples_count']
    }

    for direction, cols in influence_types.items():
        nodes_df[direction] = 0
        for col in cols:
            if col in nodes_df.columns:
                nodes_df[direction] += nodes_df[col]

    # 7. 处理缺失值
    print("\n7. Dealing missing")
    numeric_cols = nodes_df.select_dtypes(include=[np.number]).columns
    nodes_df[numeric_cols] = nodes_df[numeric_cols].fillna(0)
    remaining_nulls = nodes_df.isnull().sum().sum()
    print(f"Remain missing: {remaining_nulls}")

    # 8. 特征标准化和显示结果
    print("\n8. Standardization.")
    cols_to_scale = ['degree', 'collaboration_count', 'influence_out', 'influence_in']
    existing_cols = [col for col in cols_to_scale if col in nodes_df.columns]

    if existing_cols:
        scaler = StandardScaler()
        nodes_df[[f'{col}_scaled' for col in existing_cols]] = scaler.fit_transform(
            nodes_df[existing_cols]
        )
        print(f"standardized: {existing_cols}")

        # 显示Sailor Shift的结果
        sailor_data = nodes_df[nodes_df['node_id'] == sailor_id].iloc[0]
        print(f"\n=== Sailor Shift ===")
        print(f"Degree: {sailor_data['degree']}")
        print(f"Collabrations: {sailor_data['collaboration_count']}")
        print(f"Influence others: {sailor_data['influence_out']}")
        print(f"Influenced by others: {sailor_data['influence_in']}")

    # 9. 提取Sailor的ego网络
    print("\n9. Getting Sailor Shift ego network")
    sailor_neighbors = list(G.neighbors(sailor_id))
    sailor_ego_nodes = [sailor_id] + sailor_neighbors
    sailor_ego_df = nodes_df[nodes_df['node_id'].isin(sailor_ego_nodes)]

    sailor_ego_edges = edges_df[
        (edges_df['source'] == sailor_id) | 
        (edges_df['target'] == sailor_id) |
        (edges_df['source'].isin(sailor_neighbors) & edges_df['target'].isin(sailor_neighbors))
    ]

    print(f"ego network size: {len(sailor_ego_df)} nodes, {len(sailor_ego_edges)} edges")


    print(f"\nFinal shape:")
    print(f"nodes: {nodes_df.shape}")
    print(f"edges: {edges_df.shape}")
    return


@app.cell
def _(mo):
    mo.md(r"""
    2a.Was this influence intermittent or did it have a gradual rise?
    """)
    return


@app.cell
def _(nodes_df):
    of_works = nodes_df[
        (nodes_df['genre'] == 'Oceanus Folk') & 
        (nodes_df['node_type'].isin(['Song', 'Album']))
    ]
    of_ids = of_works['node_id'].tolist()

    print("=" * 50)
    print("Oceanus Folk Dataset Overview")
    print("=" * 50)
    print(f"Total works: {len(of_works)}")
    print(f"Year range: {of_works['release_year'].min():.0f} - {of_works['release_year'].max():.0f}")
    print(f"Songs: {len(of_works[of_works['node_type'] == 'Song'])}")
    print(f"Albums: {len(of_works[of_works['node_type'] == 'Album'])}")
    return (of_ids,)


@app.cell
def _(alt, edges_df, mo, nodes_df, of_ids):
    lnk_edges = edges_df[
        (edges_df['target'].isin(of_ids)) &
        (edges_df['edge_type'].isin(['InStyleOf', 'CoverOf', 'DirectlySamples',
                                      'InterpolatesFrom', 'LyricalReferenceTo']))
    ]

    lnk_src = nodes_df[
        nodes_df['node_id'].isin(lnk_edges['source'])
    ][['node_id', 'genre', 'release_year']].copy()
    lnk_src = lnk_src[lnk_src['genre'] != 'Oceanus Folk'].dropna(subset=['release_year'])
    lnk_src['year'] = lnk_src['release_year'].astype(int).astype(str)

    lnk_stacked = lnk_src.groupby(['year', 'genre'])['node_id'].count().reset_index()
    lnk_stacked.columns = ['year', 'genre', 'count']
    lnk_top_genres = lnk_stacked.groupby('genre')['count'].sum().nlargest(6).index.tolist()
    lnk_stacked['genre_grouped'] = lnk_stacked['genre'].apply(
        lambda x: x if x in lnk_top_genres else 'Other'
    )
    lnk_stacked2 = lnk_stacked.groupby(['year', 'genre_grouped'])['count'].sum().reset_index()

    lnk_genre_counts = lnk_src['genre'].value_counts().reset_index()
    lnk_genre_counts.columns = ['genre', 'count']
    lnk_genre_counts = lnk_genre_counts.head(10)
    lnk_genre_counts['genre_grouped'] = lnk_genre_counts['genre'].apply(
        lambda x: x if x in lnk_top_genres else 'Other'
    )

    lnk_src_counts = lnk_edges.groupby('source')['target'].count().reset_index()
    lnk_src_counts.columns = ['node_id', 'influenced_count']
    lnk_perf = edges_df[
        (edges_df['target'].isin(lnk_src_counts['node_id'])) &
        (edges_df['edge_type'] == 'PerformerOf')
    ]
    lnk_perf2 = lnk_perf.merge(lnk_src_counts, left_on='target', right_on='node_id')
    lnk_artist_top = lnk_perf2.groupby('source')['influenced_count'].sum().reset_index()
    lnk_artist_top.columns = ['node_id', 'total']
    lnk_artist_top = lnk_artist_top.merge(nodes_df[['node_id', 'name']], on='node_id')

    lnk_artist_works = edges_df[
        (edges_df['source'].isin(lnk_artist_top['node_id'])) &
        (edges_df['edge_type'] == 'PerformerOf')
    ]
    lnk_artist_work_genres = nodes_df[
        nodes_df['node_id'].isin(lnk_artist_works['target'])
    ][['node_id', 'genre']].drop_duplicates()
    lnk_artist_works2 = lnk_artist_works.merge(
        lnk_artist_work_genres, left_on='target', right_on='node_id'
    )
    lnk_artist_genre2 = lnk_artist_works2.groupby('source')['genre'].agg(
        lambda x: x.value_counts().index[0]
    ).reset_index()
    lnk_artist_genre2.columns = ['node_id', 'main_genre']

    lnk_artist_df = lnk_artist_top.merge(lnk_artist_genre2, on='node_id')
    lnk_artist_df = lnk_artist_df[lnk_artist_df['main_genre'] != 'Oceanus Folk']
    lnk_artist_df['genre_grouped'] = lnk_artist_df['main_genre'].apply(
        lambda x: x if x in lnk_top_genres else 'Other'
    )
    lnk_top5 = lnk_artist_df.groupby('genre_grouped')['total'].sum().nlargest(5).index.tolist()
    lnk_artist_df = lnk_artist_df[lnk_artist_df['genre_grouped'].isin(lnk_top5)]
    lnk_artist_grouped = lnk_artist_df.groupby('genre_grouped').apply(
        lambda x: x.nlargest(3, 'total')
    ).reset_index(drop=True)

    # ===== Selection — 一个 selection 控制所有图 =====
    lnk_selection = alt.selection_point(fields=['genre_grouped'])

    # ===== 图1：堆叠面积图 =====
    lnk_chart_area = alt.Chart(lnk_stacked2).mark_area(opacity=0.8).encode(
        x=alt.X('year:O', title='Year', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('count:Q', stack='zero', title='Works Influenced by Oceanus Folk'),
        color=alt.Color('genre_grouped:N', title='Genre'),
        opacity=alt.condition(lnk_selection, alt.value(1), alt.value(0.2)),
        tooltip=[
            alt.Tooltip('year:O', title='Year'),
            alt.Tooltip('genre_grouped:N', title='Genre'),
            alt.Tooltip('count:Q', title='Count')
        ]
    ).add_params(lnk_selection).properties(
        title='Spread of Oceanus Folk Influence Over Time by Genre',
        width=620, height=280
    )

    # ===== 图2：流派条形图 =====
    lnk_chart_bar = alt.Chart(lnk_genre_counts).mark_bar().encode(
        x=alt.X('count:Q', title='Number of Works'),
        y=alt.Y('genre:N', sort='-x', title='Genre'),
        color=alt.condition(
            lnk_selection,
            alt.Color('genre_grouped:N', legend=None),
            alt.value('lightgray')
        ),
        tooltip=['genre', 'count']
    ).properties(
        title='Genres Most Influenced by Oceanus Folk',
        width=400, height=280
    )

    # ===== 图3：艺术家条形图 =====
    lnk_chart_artist = alt.Chart(lnk_artist_grouped).mark_bar().encode(
        x=alt.X('total:Q', title='Times Influenced'),
        y=alt.Y('name:N', sort='-x', title='Artist'),
        color=alt.condition(
            lnk_selection,
            alt.Color('genre_grouped:N', legend=None),
            alt.value('lightgray')
        ),
        tooltip=['name', 'genre_grouped', 'total']
    ).properties(
        title='Top Artists Influenced by Oceanus Folk',
        width=400, height=280
    )

    # ===== 合并成一个 Altair 图 =====
    lnk_combined = lnk_chart_area & (lnk_chart_bar | lnk_chart_artist)

    mo.ui.altair_chart(lnk_combined)
    return


@app.cell
def _(edges_df, nodes_df, of_ids):
    # 其他流派 → InStyleOf → Oceanus Folk

    of_inspired_edges = edges_df[

        (edges_df['target'].isin(of_ids)) &

        (edges_df['edge_type'].isin(['InStyleOf', 'CoverOf', 'DirectlySamples',

                                      'InterpolatesFrom', 'LyricalReferenceTo']))

    ]


    # 取 source 的流派和年份

    of_inspired_sources = nodes_df[

        nodes_df['node_id'].isin(of_inspired_edges['source'])

    ][['node_id', 'genre', 'release_year']]


    of_inspired_sources = of_inspired_sources[of_inspired_sources['genre'] != 'Oceanus Folk']

    of_inspired_sources = of_inspired_sources.dropna(subset=['release_year'])


    # 分成 Sailor 崛起前后

    of_inspired_sources['period'] = of_inspired_sources['release_year'].apply(

        lambda x: 'After 2028' if x >= 2028 else 'Before 2028'

    )


    of_period = of_inspired_sources.groupby(['period', 'genre'])['node_id'].count().reset_index()

    of_period.columns = ['period', 'genre', 'count']


    print(of_period.sort_values('count', ascending=False).head(20))

    of_period
    return (of_period,)


@app.cell
def _(alt, of_period):
    # 只保留 top 6 流派

    top6 = of_period.groupby('genre')['count'].sum().nlargest(6).index.tolist()

    of_period_top = of_period[of_period['genre'].isin(top6)]


    chart3 = alt.Chart(of_period_top).mark_bar().encode(

        x=alt.X('count:Q', title='Number of Works'),

        y=alt.Y('genre:N', sort='-x', title='Genre'),

        color=alt.Color('period:N', 

                        title='Period',

                        scale=alt.Scale(

                            domain=['Before 2028', 'After 2028'],

                            range=['#aec7e8', '#1f77b4']

                        )),

        xOffset='period:N',

        tooltip=['genre', 'period', 'count']

    ).properties(

        title="Genres Inspiring Oceanus Folk: Before vs After Sailor's Breakthrough",

        width=500,

        height=350

    )


    chart3
    return


if __name__ == "__main__":
    app.run()
