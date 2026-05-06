import marimo

__generated_with = "0.19.2"
app = marimo.App(
    width="medium",
    layout_file="layouts/Mini-Challenge_Task_123 (3).slides.json",
)


@app.cell
def _(mo):
    mo.md(r"""
    # Sailor Shift — Music Network Analysis
    ## Setup
    Load the knowledge graph, build node/edge DataFrames, and locate Sailor Shift.
    """)
    return


@app.cell
def _():
    # ── Adjust path to your local data file ──────────────────────────

    file_path = "C:/Users/leeze/Documents/GitHub/Li_Zexuan/Visual_Group/MC1-data/MC1_graph.json"


    import marimo as mo

    import networkx as nx

    import json

    import pandas as pd

    import altair as alt

    from sklearn.preprocessing import StandardScaler

    import numpy as np


    # Load graph

    with open(file_path, 'r') as f:

        data = json.load(f)


    G = nx.node_link_graph(data, edges='links')


    # Build DataFrames from graph

    nodes_df = pd.DataFrame(

        [{'node_id': nid, **attrs} for nid, attrs in G.nodes(data=True)]

    )

    edges_df = pd.DataFrame(

        [{'source': u, 'target': v, **attrs} for u, v, attrs in G.edges(data=True)]

    )


    # Locate Sailor Shift

    sailor_row = nodes_df[nodes_df['name'] == 'Sailor Shift']

    assert len(sailor_row) > 0, "Sailor Shift not found in graph"

    sailor_id = sailor_row.iloc[0]['node_id']

    print(f"Sailor Shift node ID: {sailor_id}")

    print(f"Graph: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")
    return G, StandardScaler, alt, edges_df, mo, nodes_df, np, pd, sailor_id


@app.cell
def _(mo):
    mo.md(r"""
    ## Preprocessing
    Standardise column names, parse dates, fill missing values, compute degree and
    collaboration/influence metrics for every node, and extract Sailor Shift's ego network.
    """)
    return


@app.cell
def _(G, StandardScaler, edges_df, nodes_df, np, pd, sailor_id):
    pd.set_option('future.no_silent_downcasting', True)


    # ── Column names → lowercase_underscore ──────────────────────────

    nodes_df.columns = [c.lower().replace(' ', '_') for c in nodes_df.columns]

    edges_df.columns = [c.lower().replace(' ', '_') for c in edges_df.columns]


    # ── Parse date columns as numeric years ──────────────────────────

    for col, new_col in [('release_date', 'release_year'),

                         ('notoriety_date', 'notoriety_year'),

                         ('written_date', 'written_year')]:

        nodes_df[new_col] = pd.to_numeric(nodes_df[col], errors='coerce')


    # ── Boolean columns ───────────────────────────────────────────────

    nodes_df['notable'] = nodes_df['notable'].fillna(False).astype(bool)

    nodes_df['single']  = nodes_df['single'].fillna(False).astype(bool)


    # ── Categorical columns ───────────────────────────────────────────

    nodes_df['genre']      = nodes_df['genre'].fillna('Unknown')

    nodes_df['stage_name'] = nodes_df['stage_name'].fillna('')

    nodes_df['name']       = nodes_df['name'].fillna('Unknown')


    # ── Degree per node ───────────────────────────────────────────────

    nodes_df['degree'] = nodes_df['node_id'].map(dict(G.degree()))


    # ── Per-edge-type source/target counts ───────────────────────────

    for edge_type in edges_df['edge_type'].unique():

        et = edge_type.lower()

        src = edges_df[edges_df['edge_type'] == edge_type].groupby('source').size()

        tgt = edges_df[edges_df['edge_type'] == edge_type].groupby('target').size()

        nodes_df[f'source_{et}_count'] = nodes_df['node_id'].map(src).fillna(0)

        nodes_df[f'target_{et}_count'] = nodes_df['node_id'].map(tgt).fillna(0)


    # ── Collaboration count ───────────────────────────────────────────

    collab_types = ['performerof', 'composerof', 'producerof', 'lyricistof']

    nodes_df['collaboration_count'] = sum(

        nodes_df.get(f'source_{ct}_count', 0) + nodes_df.get(f'target_{ct}_count', 0)

        for ct in collab_types

    )


    # ── Influence in / out ────────────────────────────────────────────

    inf_cols = ['instyleof', 'lyricalreferenceto', 'interpolatesfrom', 'coverof', 'directlysamples']

    nodes_df['influence_out'] = sum(nodes_df.get(f'source_{c}_count', 0) for c in inf_cols)

    nodes_df['influence_in']  = sum(nodes_df.get(f'target_{c}_count', 0) for c in inf_cols)


    # ── Fill remaining numeric NaNs ───────────────────────────────────

    numeric_cols = nodes_df.select_dtypes(include=[np.number]).columns

    nodes_df[numeric_cols] = nodes_df[numeric_cols].fillna(0)


    # ── Standardise key metrics ───────────────────────────────────────

    scale_cols = ['degree', 'collaboration_count', 'influence_out', 'influence_in']

    scaler = StandardScaler()

    nodes_df[[f'{c}_scaled' for c in scale_cols]] = scaler.fit_transform(nodes_df[scale_cols])


    # ── Sailor Shift ego network ──────────────────────────────────────

    sailor_neighbors   = list(G.neighbors(sailor_id))

    sailor_ego_nodes   = [sailor_id] + sailor_neighbors

    sailor_ego_df      = nodes_df[nodes_df['node_id'].isin(sailor_ego_nodes)]

    sailor_ego_edges   = edges_df[

        (edges_df['source'] == sailor_id) |

        (edges_df['target'] == sailor_id) |

        (edges_df['source'].isin(sailor_neighbors) & edges_df['target'].isin(sailor_neighbors))

    ]


    print(f"Nodes: {nodes_df.shape[0]:,}  |  Edges: {edges_df.shape[0]:,}")

    print(f"Ego network: {len(sailor_ego_df)} nodes, {len(sailor_ego_edges)} edges")
    return


@app.cell
def _():
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Task 1a — Who has Sailor Shift been most influenced by over time?
    For each work Sailor released, we trace which external works she drew from
    (via InStyleOf, CoverOf, DirectlySamples, InterpolatesFrom, LyricalReferenceTo),
    and look at the genre, influence type, and age of those sources.
    """)
    return


@app.cell
def _(edges_df, nodes_df, sailor_id):
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

        columns={'source': 'sailor_work_id', 'target': 'ref_work_id', 'edge_type': 'inf_type'}

    )


    # Attach Sailor's work year

    a_influence_edges = a_influence_edges.merge(

        a_sailor_works[['sailor_work_id', 'sailor_year', 'sailor_work_name']],

        on='sailor_work_id', how='left'

    )


    # Attach referenced work info (genre, release year, name)

    a_influence_edges = a_influence_edges.merge(

        nodes_df[['node_id', 'name', 'genre', 'release_year']].rename(

            columns={'node_id': 'ref_work_id', 'name': 'ref_name', 'release_year': 'ref_year'}),

        on='ref_work_id', how='left'

    ).dropna(subset=['ref_year'])

    a_influence_edges['ref_year'] = a_influence_edges['ref_year'].astype(int)

    a_influence_edges = a_influence_edges[a_influence_edges['ref_year'] > 0]


    # Age of source when Sailor referenced it

    a_influence_edges['source_age'] = a_influence_edges['sailor_year'] - a_influence_edges['ref_year']


    # Collapse rare genres into 'Other'

    a_top_genres = a_influence_edges['genre'].value_counts().nlargest(7).index.tolist()

    a_influence_edges['genre_grouped'] = a_influence_edges['genre'].apply(

        lambda g: g if g in a_top_genres else 'Other'

    )


    # Aggregations for charts

    a_genre_yr = (

        a_influence_edges.groupby(['sailor_year', 'genre_grouped'])

        .size().reset_index(name='count')

    )

    a_genre_yr['year'] = a_genre_yr['sailor_year'].astype(str)


    a_type_yr = (

        a_influence_edges.groupby(['sailor_year', 'inf_type'])

        .size().reset_index(name='count')

    )

    a_type_yr['year'] = a_type_yr['sailor_year'].astype(str)


    a_dot_data = a_influence_edges[[

        'sailor_year', 'ref_name', 'ref_year', 'genre_grouped',

        'inf_type', 'source_age', 'sailor_work_name'

    ]].copy()

    a_dot_data['year'] = a_dot_data['sailor_year'].astype(str)


    print(f"Total influence references: {len(a_influence_edges)}")
    return a_dot_data, a_genre_yr, a_type_yr


@app.cell
def _(a_dot_data, a_genre_yr, a_type_yr, alt, mo):
    # ── Genre × year stacked bar ──────────────────────────────────────

    a_sel_genre = alt.selection_point(fields=['genre_grouped'], bind='legend')


    a_genre_bar = alt.Chart(a_genre_yr).mark_bar().encode(

        x=alt.X('year:O', title="Year of Sailor's Work", axis=alt.Axis(labelAngle=-45)),

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


    # ── Influence type × year stacked bar ────────────────────────────

    a_type_colors = {

        'InStyleOf':          '#4c78a8',

        'CoverOf':            '#e07b39',

        'InterpolatesFrom':   '#54a24b',

        'LyricalReferenceTo': '#eeca3b',

        'DirectlySamples':    '#b279a2',

    }


    a_type_bar = alt.Chart(a_type_yr).mark_bar().encode(

        x=alt.X('year:O', title="Year of Sailor's Work", axis=alt.Axis(labelAngle=-45)),

        y=alt.Y('count:Q', title=''),

        color=alt.Color('inf_type:N', title='Influence Type',

                        scale=alt.Scale(domain=list(a_type_colors.keys()),

                                        range=list(a_type_colors.values()))),

        tooltip=[

            alt.Tooltip('year:O', title="Sailor's Year"),

            alt.Tooltip('inf_type:N', title='Type'),

            alt.Tooltip('count:Q', title='References'),

        ]

    ).properties(

        title='How Sailor Referenced Others (by type)',

        width=310, height=220

    )


    # ── Dot plot — each reference, source age vs year ─────────────────

    a_dot = alt.Chart(a_dot_data).mark_circle(size=90, opacity=0.8).encode(

        x=alt.X('year:O', title="Year of Sailor's Work", axis=alt.Axis(labelAngle=-45)),

        y=alt.Y('source_age:Q', title='Age of Referenced Work (years old when cited)'),

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

        title="Each Influence Reference: How Old Was the Source When Sailor Drew On It?",

        width=640, height=260

    )


    # ── Lollipop + table ──────────────────────────────────────────────

    a_ref_table = (

        a_dot_data[['ref_name', 'genre_grouped', 'inf_type',

                    'ref_year', 'source_age', 'sailor_work_name', 'year']]

        .drop_duplicates(subset=['ref_name'])

        .sort_values('source_age', ascending=False)

        .reset_index(drop=True)

    )

    a_ref_table['count'] = 1

    a_ref_table['ref_label'] = (

        a_ref_table['ref_name'].str[:32] + '  (' + a_ref_table['genre_grouped'] + ')'

    )


    a_stem = alt.Chart(a_ref_table).mark_rule(color='#cccccc', strokeWidth=1.5).encode(

        y=alt.Y('ref_label:N', sort=alt.EncodingSortField('source_age', order='descending'),

                title='Referenced Work (genre)', axis=alt.Axis(labelLimit=280, labelFontSize=10)),

        x=alt.X('count:Q', scale=alt.Scale(domain=[0, 1.5]),

                title='Times Cited by Sailor', axis=alt.Axis(tickCount=2, values=[0, 1])),

    )


    a_head = alt.Chart(a_ref_table).mark_circle(opacity=0.9).encode(

        y=alt.Y('ref_label:N', sort=alt.EncodingSortField('source_age', order='descending')),

        x=alt.X('count:Q', scale=alt.Scale(domain=[0, 1.5])),

        color=alt.Color('genre_grouped:N', title='Genre', scale=alt.Scale(scheme='tableau10')),

        size=alt.Size('source_age:Q', title='Age of Source (yrs)', scale=alt.Scale(range=[60, 400])),

        shape=alt.Shape('inf_type:N', title='Influence Type'),

        tooltip=[

            alt.Tooltip('ref_name:N',         title='Referenced Work'),

            alt.Tooltip('genre_grouped:N',    title='Genre'),

            alt.Tooltip('inf_type:N',         title='Influence Type'),

            alt.Tooltip('ref_year:Q',         title='Source Released'),

            alt.Tooltip('source_age:Q',       title='Years Old When Cited'),

            alt.Tooltip('sailor_work_name:N', title="Sailor's Work"),

            alt.Tooltip('year:O',             title="Sailor's Year"),

        ]

    )


    a_lollipop = (a_stem + a_head).properties(

        title='Every Work That Influenced Sailor — Each Cited Exactly Once',

        width=360, height=660

    )


    a_display_table = (

        a_ref_table[['ref_name', 'genre_grouped', 'inf_type',

                     'ref_year', 'source_age', 'sailor_work_name', 'year']]

        .rename(columns={

            'ref_name':         'Referenced Work',

            'genre_grouped':    'Genre',

            'inf_type':         'Influence Type',

            'ref_year':         'Src Year',

            'source_age':       'Age (yrs)',

            'sailor_work_name': "Sailor's Work",

            'year':             "Sailor's Year",

        })

    )


    mo.vstack([

        alt.vconcat(

            alt.hconcat(a_genre_bar, a_type_bar).resolve_scale(color='independent'),

            a_dot

        ).resolve_scale(color='independent', shape='independent'),

        mo.hstack([a_lollipop, mo.ui.table(a_display_table, selection=None)], gap=2)

    ])
    return


@app.cell
def _():
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Task 1b — Who has Sailor Shift collaborated with and directly or indirectly influenced?
    We identify artists who share credits on Sailor's works (collaborators), then trace
    which artists' works reference Sailor's output directly (1 hop) or indirectly (2 hops).
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


    b_person_ids  = set(nodes_df[nodes_df['node_type'] == 'Person']['node_id'])

    b_artist_names = nodes_df[['node_id', 'name']].rename(

        columns={'node_id': 'artist_id', 'name': 'artist_name'}

    )


    # ── Sailor's own works ────────────────────────────────────────────

    b_sailor_work_ids = set(

        edges_df[

            (edges_df['source'] == sailor_id) &

            (edges_df['edge_type'].isin(b_collab_types))

        ]['target']

    )


    # ── Collaborators: other people credited on Sailor's works ────────

    b_co_edges = (

        edges_df[

            (edges_df['target'].isin(b_sailor_work_ids)) &

            (edges_df['edge_type'].isin(b_collab_types)) &

            (edges_df['source'] != sailor_id)

        ][['source', 'target', 'edge_type']]

        .rename(columns={'source': 'person_id', 'target': 'work_id', 'edge_type': 'role'})

    )

    b_co_edges = b_co_edges[b_co_edges['person_id'].isin(b_person_ids)]

    b_co_edges = b_co_edges.merge(

        nodes_df[['node_id', 'name']].rename(columns={'node_id': 'person_id', 'name': 'collab_name'}),

        on='person_id', how='left'

    )

    b_co_edges = b_co_edges.merge(

        nodes_df[['node_id', 'release_year', 'name']].rename(

            columns={'node_id': 'work_id', 'name': 'work_name'}),

        on='work_id', how='left'

    ).dropna(subset=['release_year'])

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


    # ── Direct influence (1 hop) ──────────────────────────────────────

    b_direct_inf_edges = edges_df[

        (edges_df['source'].isin(b_sailor_work_ids)) &

        (edges_df['edge_type'].isin(b_influence_types))

    ][['source', 'target', 'edge_type']].rename(

        columns={'source': 'sailor_work_id', 'target': 'influenced_work_id', 'edge_type': 'inf_type'}

    )


    b_influenced_work_ids = set(b_direct_inf_edges['influenced_work_id'])

    b_direct_performers = edges_df[

        (edges_df['target'].isin(b_influenced_work_ids)) &

        (edges_df['edge_type'] == 'PerformerOf')

    ][['source', 'target']].rename(

        columns={'source': 'artist_id', 'target': 'influenced_work_id'}

    )

    b_direct_performers = b_direct_performers[b_direct_performers['artist_id'].isin(b_person_ids)]


    b_direct_inf = (

        b_direct_inf_edges

        .merge(b_direct_performers, on='influenced_work_id', how='left')

        .merge(

            nodes_df[['node_id', 'release_year', 'genre']].rename(

                columns={'node_id': 'influenced_work_id'}),

            on='influenced_work_id', how='left'

        )

        .dropna(subset=['release_year', 'artist_id'])

    )

    b_direct_inf['year'] = b_direct_inf['release_year'].astype(int)


    b_direct_summary = (

        b_direct_inf.merge(b_artist_names, on='artist_id', how='left')

        .groupby(['artist_id', 'artist_name', 'genre'])

        .agg(refs=('influenced_work_id', 'nunique'))

        .reset_index()

        .sort_values('refs', ascending=False)

    )

    b_direct_summary = b_direct_summary[b_direct_summary['artist_id'] != sailor_id]


    # ── Indirect influence (2 hops) ───────────────────────────────────

    b_directly_influenced_ids = set(b_direct_inf_edges['influenced_work_id'])

    b_indirect_inf_edges = edges_df[

        (edges_df['source'].isin(b_directly_influenced_ids)) &

        (edges_df['edge_type'].isin(b_influence_types))

    ][['source', 'target']].rename(

        columns={'source': 'direct_work_id', 'target': 'indirect_work_id'}

    )


    b_indirect_work_ids = set(b_indirect_inf_edges['indirect_work_id'])

    b_indirect_performers = edges_df[

        (edges_df['target'].isin(b_indirect_work_ids)) &

        (edges_df['edge_type'] == 'PerformerOf')

    ][['source', 'target']].rename(

        columns={'source': 'artist_id', 'target': 'indirect_work_id'}

    )

    b_indirect_performers = b_indirect_performers[b_indirect_performers['artist_id'].isin(b_person_ids)]


    b_indirect_inf = (

        b_indirect_inf_edges

        .merge(b_indirect_performers, on='indirect_work_id', how='left')

        .merge(

            nodes_df[['node_id', 'release_year', 'genre']].rename(

                columns={'node_id': 'indirect_work_id'}),

            on='indirect_work_id', how='left'

        )

        .dropna(subset=['release_year', 'artist_id'])

    )

    b_indirect_inf['year'] = b_indirect_inf['release_year'].astype(int)


    b_indirect_summary = (

        b_indirect_inf.merge(b_artist_names, on='artist_id', how='left')

        .groupby(['artist_id', 'artist_name', 'genre'])

        .agg(refs=('indirect_work_id', 'nunique'))

        .reset_index()

        .sort_values('refs', ascending=False)

    )

    b_indirect_summary = b_indirect_summary[

        ~b_indirect_summary['artist_id'].isin(set(b_direct_summary['artist_id']) | {sailor_id})

    ]


    # ── Combined direct + indirect ────────────────────────────────────

    b_direct_summary['influence_type']   = 'Direct'

    b_indirect_summary['influence_type'] = 'Indirect'

    b_influenced_combined = pd.concat(

        [b_direct_summary, b_indirect_summary], ignore_index=True

    )


    print(f"Collaborators        : {len(b_collab_summary)}")

    print(f"Directly influenced  : {len(b_direct_summary)}")

    print(f"Indirectly influenced: {len(b_indirect_summary)}")
    return b_co_edges, b_collab_summary, b_influenced_combined


@app.cell
def _(alt, b_co_edges, b_collab_summary, b_influenced_combined, mo):
    TOP_COLLABS = 50

    b_top_collabs = b_collab_summary.head(TOP_COLLABS).copy()

    # ── Collaborator bar chart ────────────────────────────────────────
    b_collab_bar = alt.Chart(b_top_collabs).mark_bar().encode(
        x=alt.X('collaborations:Q', title='Shared Works', axis=alt.Axis(tickMinStep=1)),
        y=alt.Y('collab_name:N', sort='-x', title='Collaborator'),
        color=alt.Color('roles:N', title='Role(s)', scale=alt.Scale(scheme='set2')),
        tooltip=[
            alt.Tooltip('collab_name:N', title='Artist'),
            alt.Tooltip('collaborations:Q', title='Shared Works'),
            alt.Tooltip('roles:N', title='Role(s)'),
            alt.Tooltip('first_year:Q', title='First Year'),
            alt.Tooltip('last_year:Q', title='Last Year'),
        ]
    ).properties(
        title='Collaborators of Sailor Shift',
        width=550, height=550
    )

    # ── Dot strip — when did each collaboration happen ────────────────
    b_collab_filtered = (
        b_co_edges[b_co_edges['collab_name'].isin(b_top_collabs['collab_name'])]
        .drop_duplicates(subset=['collab_name', 'year'])
    )

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
        width=550, height=550
    )

    # ── Top influenced artists bar chart ─────────────────────────────
    TOP_INF = 12
    b_top_inf_artists = (
        b_influenced_combined.groupby('artist_name')['refs']
        .sum().nlargest(TOP_INF).index.tolist()
    )
    b_inf_bar_data = (
        b_influenced_combined[b_influenced_combined['artist_name'].isin(b_top_inf_artists)]
        .groupby(['artist_name', 'influence_type'])['refs']
        .sum().reset_index()
    )

    b_inf_bar = alt.Chart(b_inf_bar_data).mark_bar().encode(
        x=alt.X('refs:Q', title='Works Referencing Sailor', axis=alt.Axis(tickMinStep=1)),
        y=alt.Y('artist_name:N', sort='-x', title='Artist'),
        color=alt.Color('influence_type:N', title='Influence Depth',
                        scale=alt.Scale(domain=['Direct', 'Indirect'],
                                        range=['#e07b39', '#aec7e8'])),
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

    # ── Genre reach: direct vs indirect ──────────────────────────────
    b_top_genres2 = (
        b_influenced_combined.groupby('genre')['refs']
        .sum().nlargest(7).index.tolist()
    )
    b_influenced_combined['genre_grouped2'] = b_influenced_combined['genre'].apply(
        lambda x: x if x in b_top_genres2 else 'Other'
    )
    b_genre_inf_type = (
        b_influenced_combined
        .groupby(['genre_grouped2', 'influence_type'])['refs']
        .sum().reset_index()
    )

    b_stacked_reach = alt.Chart(b_genre_inf_type).mark_bar().encode(
        x=alt.X('refs:Q', title='Number of Artists Reached'),
        y=alt.Y('genre_grouped2:N', sort='-x', title='Genre'),
        color=alt.Color('influence_type:N', title='Influence Depth',
                        scale=alt.Scale(domain=['Direct', 'Indirect'],
                                        range=['#e07b39', '#aec7e8'])),
        tooltip=[
            alt.Tooltip('genre_grouped2:N', title='Genre'),
            alt.Tooltip('influence_type:N', title='Depth'),
            alt.Tooltip('refs:Q', title='Artists Reached'),
        ]
    ).properties(
        title="Sailor Shift's Influence Reach by Genre (Direct vs Indirect)",
        width=580, height=320
    )

    # ── Genre summary table ───────────────────────────────────────────
    b_genre_summary = (
        b_influenced_combined
        .groupby(['genre', 'influence_type'])['refs']
        .sum().reset_index()
        .pivot_table(index='genre', columns='influence_type', values='refs', fill_value=0)
        .reset_index()
    )
    b_genre_summary.columns.name = None
    for _col in ['Direct', 'Indirect']:
        if _col not in b_genre_summary.columns:
            b_genre_summary[_col] = 0
    b_genre_summary['Total'] = b_genre_summary['Direct'] + b_genre_summary['Indirect']
    b_genre_summary = b_genre_summary.sort_values('Total', ascending=False)
    b_genre_summary = b_genre_summary.rename(columns={'genre': 'Genre'})

    mo.vstack([
        alt.hconcat(b_collab_bar, b_dot_strip).resolve_scale(color='independent'),
        mo.hstack([
            b_inf_bar,
            mo.vstack([
                mo.md("**Genre breakdown of influenced artists**"),
                mo.ui.table(b_genre_summary, selection=None)
            ])
        ], gap=2),
        mo.ui.altair_chart(b_stacked_reach)
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Task 1c — How has Sailor Shift influenced the broader Oceanus Folk community?
    We look at three questions the data can answer:
    - Did the OF community grow after Sailor's 2028 breakthrough, and are new OF artists connected to her network?
    - Within the OF internal citation network, are Sailor's collaborators' works the most referenced?
    - What is the Ivy Echoes legacy — the band Sailor formed?
    """)
    return


@app.cell
def _(edges_df, nodes_df, of_ids, sailor_id):
    c_collab_types    = ['PerformerOf', 'ComposerOf', 'ProducerOf', 'LyricistOf']

    c_influence_types = ['InStyleOf', 'CoverOf', 'DirectlySamples',

                         'InterpolatesFrom', 'LyricalReferenceTo']

    BREAKTHROUGH = 2028

    c_of_set = set(of_ids)


    # Sailor's works and collaborator IDs

    c_sailor_work_ids = set(edges_df[

        (edges_df['source'] == sailor_id) &

        (edges_df['edge_type'].isin(c_collab_types))

    ]['target'])


    c_collab_ids = set(edges_df[

        (edges_df['target'].isin(c_sailor_work_ids)) &

        (edges_df['edge_type'].isin(c_collab_types)) &

        (edges_df['source'] != sailor_id)

    ]['source'])


    c_collab_work_ids = set(edges_df[

        (edges_df['source'].isin(c_collab_ids)) &

        (edges_df['edge_type'].isin(c_collab_types))

    ]['target'])


    # ── Q1: OF community growth ───────────────────────────────────────

    # Debut year per OF performer

    c_of_performers = (

        edges_df[

            (edges_df['target'].isin(c_of_set)) &

            (edges_df['edge_type'] == 'PerformerOf')

        ][['source', 'target']]

        .merge(nodes_df[['node_id', 'release_year']].rename(

            columns={'node_id': 'target'}), on='target', how='left')

        .dropna(subset=['release_year'])

        .rename(columns={'source': 'person_id'})

    )

    c_of_performers['year'] = c_of_performers['release_year'].astype(int)

    c_of_performers = c_of_performers[c_of_performers['year'] > 0]


    c_of_debut = (

        c_of_performers.groupby('person_id')['year']

        .min().reset_index(name='debut_year')

    )


    # Tag connection to Sailor (collaborators + Ivy Echoes bandmates)

    ivy_band_id = 17260

    c_bandmates = set(edges_df[

        (edges_df['target'] == ivy_band_id) &

        (edges_df['edge_type'] == 'MemberOf')

    ]['source']) - {sailor_id}


    c_sailor_connected = c_collab_ids | c_bandmates

    c_of_debut['connection'] = c_of_debut['person_id'].apply(

        lambda x: 'Connected to Sailor' if x in c_sailor_connected

                  else 'Rest of OF community'

    )


    c_of_growth = (

        c_of_debut.groupby(['debut_year', 'connection'])['person_id']

        .nunique().reset_index(name='new_artists')

        .rename(columns={'debut_year': 'year'})

    )

    c_of_growth = c_of_growth[c_of_growth['year'] > 0]


    # ── Q2: OF internal citation network ─────────────────────────────

    c_of_to_of = edges_df[

        (edges_df['source'].isin(c_of_set)) &

        (edges_df['target'].isin(c_of_set)) &

        (edges_df['edge_type'].isin(c_influence_types))

    ][['source', 'target', 'edge_type']]


    c_of_indegree = (

        c_of_to_of.groupby('target').size()

        .reset_index(name='citations')

        .rename(columns={'target': 'work_id'})

        .merge(nodes_df[['node_id', 'name', 'release_year', 'notable']].rename(

            columns={'node_id': 'work_id'}), on='work_id', how='left')

        .dropna(subset=['release_year'])

    )

    c_of_indegree['year'] = c_of_indegree['release_year'].astype(int)

    c_of_indegree = c_of_indegree[c_of_indegree['year'] > 0]

    c_of_indegree['group'] = c_of_indegree['work_id'].isin(c_collab_work_ids).map(

        {True: "Sailor's collaborator's work", False: 'Other OF work'}

    )


    # ── Q3: Ivy Echoes legacy ─────────────────────────────────────────

    ivy_work_ids = set(edges_df[

        (edges_df['source'] == ivy_band_id) &

        (edges_df['edge_type'] == 'PerformerOf')

    ]['target'])


    c_ivy_works = (

        nodes_df[nodes_df['node_id'].isin(ivy_work_ids)]

        [['node_id', 'name', 'release_year', 'notable']]

        .dropna(subset=['release_year'])

    )

    c_ivy_works['year'] = c_ivy_works['release_year'].astype(int)


    print(f"OF internal edges    : {len(c_of_to_of)}")

    print(f"Ivy Echoes works     : {len(c_ivy_works)}")

    print(f"OF artist debuts:")

    print(c_of_debut.groupby('connection')['person_id'].nunique())
    return BREAKTHROUGH, c_of_growth


@app.cell
def _(BREAKTHROUGH, alt, c_of_growth, mo, pd):
    all_years      = list(range(2015, 2041))

    all_connections = ['Connected to Sailor', 'Rest of OF community']

    c_year_sort    = [str(y) for y in all_years]


    # Fill missing year/connection combinations with 0

    c_full_index = pd.DataFrame([

        {'year': y, 'connection': c}

        for y in all_years for c in all_connections

    ])

    c_filled = (

        c_full_index

        .merge(c_of_growth, on=['year', 'connection'], how='left')

        .fillna({'new_artists': 0})

    )


    # Percentage share per year

    c_totals = c_filled.groupby('year')['new_artists'].sum().reset_index(name='total')

    c_filled  = c_filled.merge(c_totals, on='year')

    c_filled['pct']      = c_filled.apply(

        lambda r: r['new_artists'] / r['total'] * 100 if r['total'] > 0 else 0, axis=1

    )

    c_filled['year_str'] = c_filled['year'].astype(str)


    c_color_scale = alt.Scale(

        domain=['Connected to Sailor', 'Rest of OF community'],

        range=['#e07b39', '#c5c5c5']

    )


    # Breakthrough rule + label

    c_vline = alt.Chart(pd.DataFrame({'x': [str(BREAKTHROUGH)]})).mark_rule(

        strokeDash=[5, 3], color='#333', strokeWidth=2

    ).encode(x=alt.X('x:O', sort=c_year_sort))


    c_label = alt.Chart(pd.DataFrame({

        'x': [str(BREAKTHROUGH)], 'y': [85], 'text': ["← 2028 breakthrough"]

    })).mark_text(align='left', dx=5, fontSize=10, color='#333').encode(

        x=alt.X('x:O', sort=c_year_sort), y='y:Q', text='text:N'

    )


    # ── Absolute stacked bar ──────────────────────────────────────────

    c_abs_bar = alt.Chart(c_filled).mark_bar().encode(

        x=alt.X('year_str:O', sort=c_year_sort, title='',

                 axis=alt.Axis(labels=False)),

        y=alt.Y('new_artists:Q', stack='zero', title='New Artists (n)'),

        color=alt.Color('connection:N', legend=None, scale=c_color_scale),

        tooltip=[

            alt.Tooltip('year_str:O',    title='Year'),

            alt.Tooltip('connection:N',  title='Group'),

            alt.Tooltip('new_artists:Q', title='New Artists'),

        ]

    ).properties(width=660, height=100)


    # ── Relative 100% stacked bar ─────────────────────────────────────

    c_rel_bar = alt.Chart(c_filled).mark_bar().encode(

        x=alt.X('year_str:O', sort=c_year_sort, title='Year',

                 axis=alt.Axis(labelAngle=-45)),

        y=alt.Y('pct:Q', stack='zero', title='Share of New OF Artists (%)',

                 scale=alt.Scale(domain=[0, 100])),

        color=alt.Color('connection:N', title='', scale=c_color_scale),

        tooltip=[

            alt.Tooltip('year_str:O',    title='Year'),

            alt.Tooltip('connection:N',  title='Group'),

            alt.Tooltip('pct:Q',         title='Share (%)', format='.1f'),

            alt.Tooltip('new_artists:Q', title='Count'),

        ]

    ).properties(width=660, height=220)


    # ── Compose layout ────────────────────────────────────────────────

    c_growth_chart = alt.vconcat(

        (c_abs_bar + c_vline).properties(

            title='New Oceanus Folk Artists Per Year — Orange = Connected to Sailor'

        ),

        c_rel_bar + c_vline + c_label

    ).resolve_scale(color='independent')


    mo.vstack([

        mo.ui.altair_chart(c_growth_chart),

        mo.callout(mo.md(

            "The **absolute** chart (top) shows the genre peaked at 125 new artists in 2023, "

            "before Sailor's breakthrough. The **relative** chart (bottom) shows Sailor-connected "

            "artists as a larger share of new OF debutants **after 2028**."

        ), kind='info'),

    ])
    return


@app.cell
def _():
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Task 2a — Was this influence intermittent or did it have a gradual rise?
    """)
    return


@app.cell
def _(nodes_df):
    """
    Oceanus Folk Influence Analysis
    Data Preparation - Run this cell first
    """
    # Define Oceanus Folk work IDs
    of_works_ids = nodes_df[nodes_df['genre'] == 'Oceanus Folk']['node_id'].tolist()

    # Define influence edge types
    influence_edge_types = ['InStyleOf', 'CoverOf', 'DirectlySamples', 
                            'InterpolatesFrom', 'LyricalReferenceTo']

    print(f"Oceanus Folk works: {len(of_works_ids)}")
    print(f"Influence types: {influence_edge_types}")
    return influence_edge_types, of_works_ids


@app.cell
def _(alt, edges_df, influence_edge_types, mo, nodes_df, of_works_ids, pd):
    """
    QUESTION 1: Influence Growth Pattern (Task 2.3.1)
    Analyzes whether Oceanus Folk influence spread intermittently or through gradual rise
    """

    # -------------------------------
    # 1. Identify influence edges
    # -------------------------------
    of_outgoing_edges = edges_df[
        (edges_df['source'].isin(of_works_ids)) &
        (edges_df['edge_type'].isin(influence_edge_types))
    ]

    # -------------------------------
    # 2. Get unique influenced works
    # -------------------------------
    influenced_works_unique = (
        of_outgoing_edges[['target']]
        .drop_duplicates()
        .merge(
            nodes_df[['node_id', 'release_year']]
            .rename(columns={'node_id': 'target'}),
            on='target',
            how='left'
        )
    )

    # -------------------------------
    # 3. Clean year data
    # -------------------------------
    influenced_works_unique = influenced_works_unique[
        influenced_works_unique['release_year'].notna()
    ]

    influenced_works_unique['year'] = influenced_works_unique['release_year'].astype(int)

    # -------------------------------
    # 4. Aggregate yearly data
    # -------------------------------
    yearly_counts = (
        influenced_works_unique
        .groupby('year')
        .size()
        .reset_index(name='new_works')
    )

    # 确保按年份排序
    yearly_counts = yearly_counts.sort_values('year')

    # 累计
    yearly_counts['cumulative'] = yearly_counts['new_works'].cumsum()

    # -------------------------------
    # 5. Identify peak years
    # -------------------------------
    peak_year = yearly_counts.loc[yearly_counts['new_works'].idxmax(), 'year']
    peak_value = yearly_counts['new_works'].max()

    print("=" * 60)
    print("TASK 2.3.1: INFLUENCE GROWTH PATTERN ANALYSIS")
    print("=" * 60)
    print(f"Total unique works influenced: {yearly_counts['cumulative'].iloc[-1]}")
    print(f"Year range: {yearly_counts['year'].min()} - {yearly_counts['year'].max()}")
    print(f"Peak influence year: {peak_year} with {peak_value} works")
    print(f"Before 2023 avg: {yearly_counts[yearly_counts['year'] < 2023]['new_works'].mean():.1f} works/year")
    print(f"After 2023 avg: {yearly_counts[yearly_counts['year'] > 2023]['new_works'].mean():.1f} works/year")

    print("\nYearly breakdown:")
    print(yearly_counts.to_string(index=False))


    # -------------------------------
    # 6. Visualization - Intermittent, Burst-Driven Pattern
    # -------------------------------

    # ===== CUMULATIVE LINE =====
    cumulative_growth_chart = alt.Chart(yearly_counts).mark_line(
        color='#e07b39',
        strokeWidth=3,
        point=alt.OverlayMarkDef(filled=True, fill='white', size=60)
    ).encode(
        x=alt.X('year:Q', title='Year', axis=alt.Axis(format='d')),
        y=alt.Y('cumulative:Q', title='Cumulative Works Influenced'),
        tooltip=['year', 'cumulative', 'new_works']
    ).properties(
        title='Cumulative Growth of Oceanus Folk Influence',
        width=600,
        height=400
    )

    # ===== MARK BURST YEARS =====
    # 2023 - 最大爆发
    burst_2023_line = alt.Chart(
        pd.DataFrame({'year': [2023]})
    ).mark_rule(
        color='#e07b39',
        strokeDash=[5, 5],
        strokeWidth=2
    ).encode(x='year:Q')

    # 2028 - Sailor's breakthrough
    breakthrough_2028_line = alt.Chart(
        pd.DataFrame({'year': [2028]})
    ).mark_rule(
        color='red',
        strokeDash=[5, 5],
        strokeWidth=2
    ).encode(x='year:Q')

    # ===== ANNOTATIONS =====
    # 2023 峰值标注
    if 2023 in yearly_counts['year'].values:
        val_at_2023 = yearly_counts.loc[
            yearly_counts['year'] == 2023, 'cumulative'
        ].iloc[0]
        burst_annotation = alt.Chart(
            pd.DataFrame({
                'year': [2023],
                'cumulative': [val_at_2023],
                'text': [f"Peak Burst ({peak_value} works, 2023)"]
            })
        ).mark_text(
            align='right',
            baseline='bottom',
            dx=-10,
            dy=-5,
            fontSize=11,
            color='#e07b39',
            fontWeight='bold'
        ).encode(
            x='year:Q',
            y='cumulative:Q',
            text='text'
        )
    else:
        burst_annotation = alt.Chart(pd.DataFrame()).mark_text()

    # 2028 突破标注
    if 2028 in yearly_counts['year'].values:
        val_at_2028 = yearly_counts.loc[
            yearly_counts['year'] == 2028, 'cumulative'
        ].iloc[0]
        breakthrough_annotation = alt.Chart(
            pd.DataFrame({
                'year': [2028],
                'cumulative': [val_at_2028],
                'text': ["Sailor's Breakthrough (2028)"]
            })
        ).mark_text(
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
    else:
        breakthrough_annotation = alt.Chart(pd.DataFrame()).mark_text()

    # ===== ANNUAL BAR CHART - 突出爆发式模式 =====
    # 分类数据用于不同颜色
    before_2023 = yearly_counts[yearly_counts['year'] < 2023]
    burst_2023 = yearly_counts[yearly_counts['year'] == 2023]
    between_2023_2028 = yearly_counts[(yearly_counts['year'] > 2023) & (yearly_counts['year'] < 2028)]
    after_2028 = yearly_counts[yearly_counts['year'] > 2028]
    breakthrough_2028 = yearly_counts[yearly_counts['year'] == 2028]

    # 长期停滞期 (1980-2022) - 灰色
    stagnation_bars = alt.Chart(before_2023).mark_bar(color='#d3d3d3').encode(
        x=alt.X('year:Q', title='Year', axis=alt.Axis(format='d')),
        y=alt.Y('new_works:Q', title='New Works Influenced per Year'),
        tooltip=['year', 'new_works', 'cumulative']
    )

    # 2023 爆发峰值 - 橙色高亮
    peak_bars = alt.Chart(burst_2023).mark_bar(color='#e07b39', stroke='black', strokeWidth=1).encode(
        x='year:Q',
        y='new_works:Q',
        tooltip=['year', 'new_works', 'cumulative']
    )

    # 2024-2027 间期 - 浅橙色
    interim_bars = alt.Chart(between_2023_2028).mark_bar(color='#f0b27a').encode(
        x='year:Q',
        y='new_works:Q',
        tooltip=['year', 'new_works', 'cumulative']
    )

    # 2028 突破年 - 红色
    breakthrough_bars = alt.Chart(breakthrough_2028).mark_bar(color='#ff6b6b').encode(
        x='year:Q',
        y='new_works:Q',
        tooltip=['year', 'new_works', 'cumulative']
    )

    # 2029+ 后续影响 - 深橙色
    after_bars = alt.Chart(after_2028).mark_bar(color='#e07b39', opacity=0.7).encode(
        x='year:Q',
        y='new_works:Q',
        tooltip=['year', 'new_works', 'cumulative']
    )

    # 组合所有图层
    annual_new_chart = alt.layer(
        stagnation_bars, peak_bars, interim_bars, breakthrough_bars, after_bars
    ).properties(
        title='Annual New Works Influenced by Oceanus Folk (Burst-Driven Pattern)',
        width=600,
        height=400
    )

    # ===== FINAL COMBINATION =====
    t2a_combined = alt.hconcat(
        cumulative_growth_chart + burst_2023_line + breakthrough_2028_line + burst_annotation + breakthrough_annotation,
        annual_new_chart
    )

    # ===== DISPLAY =====
    mo.vstack([
        mo.ui.altair_chart(t2a_combined),
        mo.callout(
            mo.md(
                f"""
                **Key finding:** Oceanus Folk's influence follows an **intermittent, burst-driven pattern** rather than a gradual rise.
            
                ### Evidence for this Pattern:
                - **1980-2005:** Nearly horizontal cumulative curve with minimal annual activity
                - **Peak burst in {peak_year}:** {peak_value} works influenced in a single year—the genre's largest impact
                -  The cumulative curve shows clear step-like increases during burst years
                -  Other distinct bursts visible around 2010, 2017, and 2028
            
                ### Conclusion:
                This pattern definitively rejects the hypothesis of a smooth or gradual rise. Instead, the genre's 
                expansion was triggered by specific cultural moments or influential releases, with the {peak_year} burst 
                representing the maximum cross-genre impact—occurring five years before Sailor Shift's 2028 breakthrough.
                """,
            ),
            kind='info'
        )
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Task 2b What genres and top artists have been most influenced by Oceanus Folk?
    """)
    return


@app.cell
def _(alt, edges_df, influence_edge_types, mo, nodes_df, of_works_ids, pd):
    """
    QUESTION 2: Most Influenced Genres and Artists (Task 2.3.2) - 最终交互版
    """

    # 1. 数据准备
    of_outgoing_edges_q2 = edges_df[
        (edges_df['source'].isin(of_works_ids)) &
        (edges_df['edge_type'].isin(influence_edge_types))
    ]

    influenced_works_q2 = nodes_df[
        nodes_df['node_id'].isin(of_outgoing_edges_q2['target'])
    ][['node_id', 'genre', 'release_year']].copy()

    influenced_works_q2 = influenced_works_q2[
        (influenced_works_q2['genre'] != 'Oceanus Folk') &
        (influenced_works_q2['release_year'].notna())
    ]
    influenced_works_q2['year'] = influenced_works_q2['release_year'].astype(int)

    # 2. 面积图数据
    genre_yearly_q2 = influenced_works_q2.groupby(['year', 'genre']).size().reset_index(name='count')
    top_genres_q2 = genre_yearly_q2.groupby('genre')['count'].sum().nlargest(6).index.tolist()
    genre_yearly_q2['genre_grouped'] = genre_yearly_q2['genre'].apply(
        lambda x: x if x in top_genres_q2 else 'Other'
    )
    genre_stacked_q2 = genre_yearly_q2.groupby(['year', 'genre_grouped'])['count'].sum().reset_index()
    genre_stacked_q2['genre_grouped'] = genre_stacked_q2['genre_grouped'].astype(str)

    # 3. 条形图数据（流派）
    genre_counts_q2 = influenced_works_q2['genre'].value_counts().head(10).reset_index()
    genre_counts_q2.columns = ['genre', 'count']
    genre_counts_q2['genre_grouped'] = genre_counts_q2['genre'].apply(
        lambda x: x if x in top_genres_q2 else 'Other'
    ).astype(str)

    # 4. 艺术家数据
    unique_targets_q2 = of_outgoing_edges_q2[['target']].drop_duplicates()
    artist_works_q2 = edges_df[
        (edges_df['target'].isin(unique_targets_q2['target'])) &
        (edges_df['edge_type'] == 'PerformerOf')
    ][['source', 'target']].rename(columns={'source': 'artist_id', 'target': 'work_id'})
    artist_works_q2 = artist_works_q2[
        artist_works_q2['artist_id'].isin(nodes_df[nodes_df['node_type'] == 'Person']['node_id'])
    ]
    artist_counts_q2 = artist_works_q2.groupby('artist_id')['work_id'].nunique().reset_index(name='total')
    artist_df_q2 = artist_counts_q2.merge(
        nodes_df[['node_id', 'name']].rename(columns={'node_id': 'artist_id'}),
        on='artist_id'
    )

    # 艺术家主要流派
    artist_all_q2 = edges_df[
        (edges_df['source'].isin(artist_df_q2['artist_id'])) &
        (edges_df['edge_type'] == 'PerformerOf')
    ]
    work_genres_q2 = nodes_df[nodes_df['node_id'].isin(artist_all_q2['target'])][['node_id', 'genre']].drop_duplicates()
    artist_genres_q2 = artist_all_q2.merge(work_genres_q2, left_on='target', right_on='node_id')
    main_genre_q2 = artist_genres_q2.groupby('source')['genre'].agg(lambda x: x.value_counts().index[0]).reset_index()
    main_genre_q2.columns = ['artist_id', 'main_genre']
    artist_df_q2 = artist_df_q2.merge(main_genre_q2, on='artist_id')
    artist_df_q2 = artist_df_q2[artist_df_q2['main_genre'] != 'Oceanus Folk']
    artist_df_q2['genre_grouped'] = artist_df_q2['main_genre'].apply(
        lambda x: x if x in top_genres_q2 else 'Other'
    ).astype(str)
    top_artists_q2 = artist_df_q2.nlargest(10, 'total')

    # 5. 创建独立的图例数据
    legend_data_q2 = pd.DataFrame({'genre_grouped': top_genres_q2 + ['Other']})

    # 6. 交互选择器
    selector_q2 = alt.selection_point(
        fields=['genre_grouped'],
        name='selector_task2_q2'  # 唯一名称
    )

    # 7. 独立的图例图层（可点击）
    legend_chart_q2 = alt.Chart(legend_data_q2).mark_rect().encode(
        y=alt.Y('genre_grouped:N', title='Click to filter genres'),
        color=alt.Color('genre_grouped:N', title='Legend', scale=alt.Scale(scheme='tableau10')),
        opacity=alt.condition(selector_q2, alt.value(1), alt.value(0.3))
    ).add_params(selector_q2).properties(width=100, height=280)

    # 8. 面积图（不显示图例）
    area_q2 = alt.Chart(genre_stacked_q2).mark_area(opacity=0.8).encode(
        x=alt.X('year:Q', title='Year', axis=alt.Axis(format='d')),
        y=alt.Y('count:Q', stack='zero', title='Works Influenced'),
        color=alt.Color('genre_grouped:N', legend=None, scale=alt.Scale(scheme='tableau10')),
        opacity=alt.condition(selector_q2, alt.value(1), alt.value(0.2)),
        tooltip=['year', 'genre_grouped', 'count']
    ).add_params(selector_q2).properties(width=500, height=280)

    # 9. 面积图标注（峰值和突破）- 使用唯一变量名
    yearly_total_q2 = influenced_works_q2.groupby('year').size().reset_index(name='count')
    peak_year_q2 = yearly_total_q2.loc[yearly_total_q2['count'].idxmax(), 'year']
    peak_value_q2 = yearly_total_q2.loc[yearly_total_q2['count'].idxmax(), 'count']

    print(f"Peak year: {peak_year_q2}, Peak value: {peak_value_q2} works")  # 应该输出 2023: 25

    if peak_year_q2 == 2023:
        peak_annot_q2 = alt.Chart(pd.DataFrame({
            'year': [2023], 'count': [peak_value_q2], 'text': [f'Peak {peak_value_q2} works (2023)']
        })).mark_text(align='right', baseline='bottom', dx=-10, dy=-10, color='#e07b39', fontSize=10).encode(
            x='year:Q', y='count:Q', text='text'
        )
    else:
        peak_annot_q2 = alt.Chart(pd.DataFrame()).mark_text()

    break_rule_q2 = alt.Chart(pd.DataFrame({'year': [2028]})).mark_rule(
        color='red', strokeDash=[5, 5], strokeWidth=2
    ).encode(x='year:Q')

    if 2028 in yearly_total_q2['year'].values:
        val_2028_q2 = yearly_total_q2[yearly_total_q2['year'] == 2028]['count'].iloc[0]
        break_annot_q2 = alt.Chart(pd.DataFrame({
            'year': [2028], 'count': [val_2028_q2], 'text': ["Sailor's Breakthrough (2028)"]
        })).mark_text(align='left', baseline='top', dx=10, dy=-5, fontSize=11, color='red').encode(
            x='year:Q', y='count:Q', text='text'
        )
    else:
        break_annot_q2 = alt.Chart(pd.DataFrame()).mark_text()

    area_q2 = area_q2 + break_rule_q2 + peak_annot_q2 + break_annot_q2

    # 10. 流派条形图
    bar_genres_q2 = alt.Chart(genre_counts_q2).mark_bar().encode(
        x=alt.X('count:Q', title='Number of Works'),
        y=alt.Y('genre:N', sort='-x', title='Genre'),
        color=alt.Color('genre_grouped:N', legend=None, scale=alt.Scale(scheme='tableau10')),
        opacity=alt.condition(selector_q2, alt.value(1), alt.value(0.2)),
        tooltip=['genre', 'count']
    ).add_params(selector_q2).properties(width=400, height=280)

    # 11. 艺术家条形图
    bar_artists_q2 = alt.Chart(top_artists_q2).mark_bar().encode(
        x=alt.X('total:Q', title='Number of Influenced Works'),
        y=alt.Y('name:N', sort='-x', title='Artist'),
        color=alt.Color('genre_grouped:N', legend=None, scale=alt.Scale(scheme='tableau10')),
        opacity=alt.condition(selector_q2, alt.value(1), alt.value(0.2)),
        tooltip=['name', 'main_genre', 'total']
    ).add_params(selector_q2).properties(width=400, height=280)

    # 12. 组合：左侧图例 + 右侧上方面积图 + 右侧下方两个条形图
    right_panel_q2 = alt.vconcat(area_q2, alt.hconcat(bar_genres_q2, bar_artists_q2))
    combined_q2 = alt.hconcat(legend_chart_q2, right_panel_q2)

    mo.ui.altair_chart(combined_q2)

    # ===== DISPLAY =====
    # 计算关键统计数据用于文本
    top_genre = influenced_works_q2['genre'].value_counts().index[0]
    top_genre_count = influenced_works_q2['genre'].value_counts().iloc[0]
    second_genre = influenced_works_q2['genre'].value_counts().index[1] if len(influenced_works_q2['genre'].value_counts()) > 1 else "N/A"
    second_genre_count = influenced_works_q2['genre'].value_counts().iloc[1] if len(influenced_works_q2['genre'].value_counts()) > 1 else 0

    # 计算被影响最多的艺术家
    top_artist_name = top_artists_q2.iloc[0]['name'] if len(top_artists_q2) > 0 else "N/A"
    top_artist_count = top_artists_q2.iloc[0]['total'] if len(top_artists_q2) > 0 else 0

    mo.vstack([
        mo.ui.altair_chart(combined_q2),
        mo.callout(
            mo.md(
                f"""
                **Key finding:** Oceanus Folk's influence is both **deep and broad**, reaching beyond its home genre into diverse musical territories.
            
                ### Most Influenced Genres:
                - **{top_genre} ({top_genre_count} works):** The most heavily impacted specific genre, confirming Oceanus Folk as a foundational pillar within the modern folk movement
                - **{second_genre} ({second_genre_count} works):** Significant influence in atmospheric and electronic-leaning styles, suggesting Oceanus Folk's textures are highly compatible with modern production
                - **Dream Pop (15 works):** Strong presence in ethereal, effects-driven styles
                - **"Other" category (24 works):** The largest total group, indicating a wide "long-tail" distribution across numerous niche sub-genres
            
                ### Most Influenced Artists:
                - **{top_artist_name} ({top_artist_count} works):** The most influenced individual artist, with {top_artist_count} distinct works directly attributed to Oceanus Folk's influence
                - **Dense secondary tier (2 works each):** Artists including Guiying Liao, Yan Zou, Tao Hu, and Jun Zhou demonstrate that influence is decentralized and widespread
            
                ### Conclusion:
                The influence of Oceanus Folk is both deep (concentrated in Indie Folk) and broad (extending into Synthwave and Dream Pop). The widespread impact across a diverse range of artists proves that the genre has successfully transitioned from a niche style into a versatile source of inspiration for both mainstream and experimental creators.
                """
            ),
            kind='info'
        )
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Task 2c.  How has Oceanus Folk changed with the rise of Sailor Shift? From which genres does it draw most of its contemporary inspiration?
    """)
    return


@app.cell
def _(alt, edges_df, mo, nodes_df):
    """
    QUESTION 3: How Oceanus Folk Changed
    Analyzes which genres influenced Oceanus Folk before vs after 2028
    This cell is completely independent - no dependencies on other cells
    """

    # Define Oceanus Folk work IDs locally
    of_works_ids_q3 = nodes_df[nodes_df['genre'] == 'Oceanus Folk']['node_id'].tolist()

    # Define influence edge types locally
    influence_edge_types_q3 = ['InStyleOf', 'CoverOf', 'DirectlySamples', 
                               'InterpolatesFrom', 'LyricalReferenceTo']

    # Identify edges where Oceanus Folk is influenced by others
    of_incoming_edges_q3 = edges_df[
        (edges_df['target'].isin(of_works_ids_q3)) &
        (edges_df['edge_type'].isin(influence_edge_types_q3))
    ]

    print(f"Edges where Oceanus Folk is influenced: {len(of_incoming_edges_q3)}")

    # Extract source works (influencing works)
    influencing_works_q3 = nodes_df[
        nodes_df['node_id'].isin(of_incoming_edges_q3['source'])
    ][['node_id', 'genre', 'release_year']].copy()

    influencing_works_q3 = influencing_works_q3[
        (influencing_works_q3['genre'] != 'Oceanus Folk') &
        (influencing_works_q3['release_year'].notna())
    ]

    print(f"Unique works influencing Oceanus Folk: {len(influencing_works_q3)}")

    # Categorize by period
    influencing_works_q3['period'] = influencing_works_q3['release_year'].apply(
        lambda x: 'After 2028' if x >= 2028 else 'Before 2028'
    )

    # Aggregate counts
    period_genre_counts_q3 = influencing_works_q3.groupby(['period', 'genre']).size().reset_index(name='count')

    # Print summary
    print("\n" + "=" * 60)
    print("GENRES INFLUENCING OCEANUS FOLK")
    print("=" * 60)
    print("\nTop 10 influencing genres overall:")
    print(period_genre_counts_q3.groupby('genre')['count'].sum().nlargest(10))

    print("\n" + "-" * 40)
    print("Before 2028 - Top 5 genres:")
    before_2028_q3 = period_genre_counts_q3[period_genre_counts_q3['period'] == 'Before 2028'].nlargest(5, 'count')
    print(before_2028_q3[['genre', 'count']].to_string(index=False))

    print("\nAfter 2028 - Top 5 genres:")
    after_2028_q3 = period_genre_counts_q3[period_genre_counts_q3['period'] == 'After 2028'].nlargest(5, 'count')
    print(after_2028_q3[['genre', 'count']].to_string(index=False))

    # Get top 6 genres for visualization
    top_genres_q3 = period_genre_counts_q3.groupby('genre')['count'].sum().nlargest(6).index.tolist()
    print(f"\nTop 6 genres for visualization: {top_genres_q3}")

    period_genre_top_q3 = period_genre_counts_q3[period_genre_counts_q3['genre'].isin(top_genres_q3)]

    # Create comparison bar chart
    comparison_chart_q3 = alt.Chart(period_genre_top_q3).mark_bar().encode(
        x=alt.X('count:Q', title='Number of Works'),
        y=alt.Y('genre:N', sort='-x', title='Genre'),
        color=alt.Color('period:N', title='Period',
                        scale=alt.Scale(domain=['Before 2028', 'After 2028'],
                                        range=['#aec7e8', '#1f77b4'])),
        xOffset='period:N',
        tooltip=['genre', 'period', 'count']
    ).properties(
        title="Genres Influencing Oceanus Folk: Before vs. After Sailor Shift's Breakthrough",
        width=500,
        height=350
    )

    # Display the chart
    comparison_chart_q3


    # ===== 计算统计数据用于显示 =====
    # 在 period_genre_counts_q3 定义之后，显示部分之前添加

    # 获取 Before 2028 和 After 2028 的统计数据
    before_data_q3 = period_genre_counts_q3[period_genre_counts_q3['period'] == 'Before 2028']
    after_data_q3 = period_genre_counts_q3[period_genre_counts_q3['period'] == 'After 2028']

    # Americana 数据
    americana_before = before_data_q3[before_data_q3['genre'] == 'Americana']['count'].sum() if 'Americana' in before_data_q3['genre'].values else 0
    americana_after = after_data_q3[after_data_q3['genre'] == 'Americana']['count'].sum() if 'Americana' in after_data_q3['genre'].values else 0

    # Dream Pop 数据
    dreampop_before = before_data_q3[before_data_q3['genre'] == 'Dream Pop']['count'].sum() if 'Dream Pop' in before_data_q3['genre'].values else 0
    dreampop_after = after_data_q3[after_data_q3['genre'] == 'Dream Pop']['count'].sum() if 'Dream Pop' in after_data_q3['genre'].values else 0

    # Indie Folk 数据
    indiefolk_before = before_data_q3[before_data_q3['genre'] == 'Indie Folk']['count'].sum() if 'Indie Folk' in before_data_q3['genre'].values else 0
    indiefolk_after = after_data_q3[after_data_q3['genre'] == 'Indie Folk']['count'].sum() if 'Indie Folk' in after_data_q3['genre'].values else 0

    # 打印调试信息确认数据
    print(f"Americana: Before {americana_before}, After {americana_after}")
    print(f"Dream Pop: Before {dreampop_before}, After {dreampop_after}")
    print(f"Indie Folk: Before {indiefolk_before}, After {indiefolk_after}")

    # ===== DISPLAY =====
    mo.vstack([
        mo.ui.altair_chart(comparison_chart_q3),
        mo.callout(
            mo.md(
                f"""
                **Key finding:** With Sailor Shift's breakthrough, Oceanus Folk took a new direction—away from its traditional roots and toward a modern, atmospheric style.
            
                ### The Disappearance of Americana
                - **Before 2028:** Americana contributed **{int(americana_before)} influence edges**
                - **After 2028:** **{int(americana_after)} recorded influence** from Americana
            
            
                ### Dream Pop & Indie Folk: The Stable Pillars
                - **Dream Pop:** Grew from {int(dreampop_before)} to **{int(dreampop_before + dreampop_after)} total works** (added {int(dreampop_after)} after 2028)
                - **Indie Folk:** Grew from {int(indiefolk_before)} to **{int(indiefolk_before + indiefolk_after)} total works** (added {int(indiefolk_after)} after 2028)
         
            
                ### Emerging Textures: Synthetic & Cinematic
                - **Synthwave** and **Desert Rock** maintained steady influence after 2028
                - **Space Rock** showed consistent presence
          
            
                ### Conclusion:
                After 2028, Oceanus Folk drew less from Americana and continued to rely on Dream Pop and Indie Folk. This shift in its own influences likely contributed to the stylistic evolution heard in works influenced by the genre during this period.
                """
            ),
            kind='info'
        )
    ])
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Task 3a — Who are the most prominent Oceanus Folk artists?
    We build an artist profile for every person in the graph by counting how many works
    they performed, composed, produced and wrote lyrics for, plus how many bands they belong to.
    From that we derive a collaboration score and influence score, then plot activity,
    popularity and influence timelines for the top Oceanus Folk artists.
    """)
    return


@app.cell
def _():
    return


@app.cell
def _(edges_df, nodes_df):
    # ── Base artist table ─────────────────────────────────────────────

    t3_artists_df = nodes_df[nodes_df['node_type'] == 'Person'].copy()

    t3_songs_df   = nodes_df[nodes_df['node_type'] == 'Song'].copy()

    t3_albums_df  = nodes_df[nodes_df['node_type'] == 'Album'].copy()


    t3_artist_profiles = t3_artists_df[['node_id', 'name', 'stage_name']].copy()


    # ── Count each role type and merge in one pass ────────────────────

    t3_role_types = {

        'PerformerOf': 'performed_works_count',

        'ComposerOf':  'composed_count',

        'LyricistOf':  'lyricist_count',

        'ProducerOf':  'producer_count',

    }


    for t3_role, t3_col in t3_role_types.items():

        t3_counts = (

            edges_df[edges_df['edge_type'] == t3_role]

            .groupby('source').size()

            .reset_index(name=t3_col)

            .rename(columns={'source': 'node_id'})

        )

        t3_artist_profiles = t3_artist_profiles.merge(t3_counts, on='node_id', how='left')

        t3_artist_profiles[t3_col] = t3_artist_profiles[t3_col].fillna(0)


    # ── Band memberships ──────────────────────────────────────────────

    t3_member_counts = (

        edges_df[edges_df['edge_type'] == 'MemberOf']

        .groupby('source').size()

        .reset_index(name='group_memberships')

        .rename(columns={'source': 'node_id'})

    )

    t3_artist_profiles = t3_artist_profiles.merge(t3_member_counts, on='node_id', how='left')

    t3_artist_profiles['group_memberships'] = t3_artist_profiles['group_memberships'].fillna(0)


    # ── Collaboration and influence scores ────────────────────────────

    t3_artist_profiles['collaboration_score'] = (

        t3_artist_profiles['performed_works_count']

        + t3_artist_profiles['group_memberships']

        + t3_artist_profiles['producer_count']

    )

    t3_artist_profiles['influence_score'] = (

        t3_artist_profiles['composed_count']

        + t3_artist_profiles['lyricist_count']

        + t3_artist_profiles['producer_count']

    )


    print(f"Artists: {len(t3_artist_profiles)}")

    print(f"\nTop 5 by collaboration score:")

    print(t3_artist_profiles.nlargest(5, 'collaboration_score')[['name', 'collaboration_score']])

    print(f"\nTop 5 by influence score:")

    print(t3_artist_profiles.nlargest(5, 'influence_score')[['name', 'influence_score']])
    return t3_artist_profiles, t3_songs_df


@app.cell
def _(edges_df, pd, t3_artist_profiles, t3_songs_df):
    # ── Artist → Song links ───────────────────────────────────────────

    # PerformerOf: source=Person, target=Song.

    # We join on target to get song metadata onto each artist-song pair.

    t3_artist_song_links = (

        edges_df[edges_df['edge_type'] == 'PerformerOf']

        .merge(

            t3_songs_df[['node_id', 'name', 'release_year', 'genre', 'notable']].rename(

                columns={'node_id': 'song_id', 'name': 'song_name'}),

            left_on='target', right_on='song_id', how='inner'

        )

        .merge(

            t3_artist_profiles[['node_id', 'name', 'stage_name']].rename(

                columns={'node_id': 'artist_id', 'name': 'artist_name',

                         'stage_name': 'artist_stage_name'}),

            left_on='source', right_on='artist_id', how='left'

        )

    )


    # ── Which artists make Oceanus Folk music? ────────────────────────

    t3_oceanus_artists = set(

        t3_artist_song_links[t3_artist_song_links['genre'] == 'Oceanus Folk']['artist_name']

    )


    # ── Activity timeline: songs released per artist per year ─────────

    t3_artist_song_links['release_year'] = pd.to_numeric(

        t3_artist_song_links['release_year'], errors='coerce'

    )

    t3_artist_yearly = (

        t3_artist_song_links

        .groupby(['artist_name', 'release_year'])

        .size()

        .reset_index(name='songs_per_year')

        .dropna(subset=['release_year'])

    )


    # ── Popularity timeline: notable songs per artist per year ────────

    t3_artist_notable_yearly = (

        t3_artist_song_links[t3_artist_song_links['notable'] == True]

        .groupby(['artist_name', 'release_year'])

        .size()

        .reset_index(name='notable_songs_per_year')

        .dropna(subset=['release_year'])

    )


    # ── Influence timeline ────────────────────────────────────────────

    # Influence edges: source=referencing work, target=referenced work.

    # We join target back to artist_song_links to find which artist

    # owns the referenced song, then count references per artist per year.

    t3_influence_edges = edges_df[

        edges_df['edge_type'].isin([

            'DirectlySamples', 'CoverOf', 'InterpolatesFrom',

            'LyricalReferenceTo', 'InStyleOf'

        ])

    ]


    t3_influence_with_artist = (

        t3_influence_edges

        .merge(

            t3_artist_song_links[['song_id', 'artist_id', 'artist_name', 'release_year']].rename(

                columns={'release_year': 'song_release_year'}),

            left_on='target', right_on='song_id', how='inner'

        )

    )


    t3_artist_influence_yearly = (

        t3_influence_with_artist

        .groupby(['artist_name', 'song_release_year'])

        .size()

        .reset_index(name='influence_per_year')

        .dropna(subset=['song_release_year'])

    )


    print(f"Oceanus Folk artists : {len(t3_oceanus_artists)}")

    print(f"Activity rows        : {len(t3_artist_yearly)}")

    print(f"Popularity rows      : {len(t3_artist_notable_yearly)}")

    print(f"Influence rows       : {len(t3_artist_influence_yearly)}")
    return (
        t3_artist_influence_yearly,
        t3_artist_notable_yearly,
        t3_artist_yearly,
        t3_oceanus_artists,
    )


@app.cell
def _(
    alt,
    mo,
    t3_artist_influence_yearly,
    t3_artist_notable_yearly,
    t3_artist_yearly,
    t3_oceanus_artists,
):
    # ── Filter to active OF artists (≥8 songs total) ──────────────────

    # Removes the long tail of artists who only appear once or twice,

    # keeping the charts readable. Same threshold as the original.

    t3_activity_of = t3_artist_yearly[

        t3_artist_yearly['artist_name'].isin(t3_oceanus_artists)

    ].copy()


    t3_active_of_artists = (

        t3_activity_of.groupby('artist_name')['songs_per_year']

        .sum()

        .loc[lambda s: s >= 8]

        .index

    )


    t3_activity_top = t3_activity_of[

        t3_activity_of['artist_name'].isin(t3_active_of_artists)

    ].copy()


    t3_popularity_top = t3_artist_notable_yearly[

        t3_artist_notable_yearly['artist_name'].isin(t3_active_of_artists) |

        (t3_artist_notable_yearly['artist_name'] == 'Sailor Shift')

    ].copy()


    t3_influence_of = t3_artist_influence_yearly[

        t3_artist_influence_yearly['artist_name'].isin(t3_oceanus_artists)

    ].copy()

    t3_influence_top = t3_influence_of[

        t3_influence_of.groupby('artist_name')['influence_per_year']

        .transform('sum') >= 20

    ].copy()


    # ── Shared selection — click artist name to highlight ─────────────

    # Defined once and shared across all three charts and the legend.

    t3_selection = alt.selection_point(fields=['artist_name'])


    # ── Clickable legend ──────────────────────────────────────────────

    t3_legend_data = t3_activity_top[['artist_name']].drop_duplicates()


    t3_legend = alt.Chart(t3_legend_data).mark_text(

        align='left', baseline='middle', dx=5

    ).encode(

        y=alt.Y('artist_name:N', axis=None, title=None),

        text=alt.Text('artist_name:N'),

        color=alt.condition(

            t3_selection,

            alt.Color('artist_name:N', legend=None),

            alt.value('lightgray')

        )

    ).add_params(t3_selection).properties(

        width=180, height=250, title='Select Artist'

    )


    # ── Activity chart ────────────────────────────────────────────────

    t3_activity_chart = alt.Chart(t3_activity_top).mark_line(point=True).encode(

        x=alt.X('release_year:Q', title='Year'),

        y=alt.Y('songs_per_year:Q', title='Songs per Year'),

        color=alt.Color('artist_name:N', legend=None),

        opacity=alt.condition(t3_selection, alt.value(1), alt.value(0.1)),

        tooltip=['artist_name', 'release_year', 'songs_per_year']

    ).add_params(t3_selection).properties(

        title='Activity Over Time', width=420, height=250

    )


    # ── Popularity chart ──────────────────────────────────────────────

    t3_popularity_chart = alt.Chart(t3_popularity_top).mark_line(point=True).encode(

        x=alt.X('release_year:Q', title='Year'),

        y=alt.Y('notable_songs_per_year:Q', title='Notable Songs per Year'),

        color=alt.Color('artist_name:N', legend=None),

        opacity=alt.condition(t3_selection, alt.value(1), alt.value(0.1)),

        tooltip=['artist_name', 'release_year', 'notable_songs_per_year']

    ).add_params(t3_selection).properties(

        title='Popularity Over Time', width=420, height=250

    )


    # ── Influence chart ───────────────────────────────────────────────

    # Sailor Shift has no incoming influence edges in the data,

    # so she does not appear here — this is expected.

    t3_influence_chart = alt.Chart(t3_influence_top).mark_line(point=True).encode(

        x=alt.X('song_release_year:Q', title='Year'),

        y=alt.Y('influence_per_year:Q', title='Influence per Year'),

        color=alt.Color('artist_name:N', legend=None),

        opacity=alt.condition(t3_selection, alt.value(1), alt.value(0.1)),

        tooltip=['artist_name', 'song_release_year', 'influence_per_year']

    ).add_params(t3_selection).properties(

        title='Influence Over Time', width=420, height=250

    )


    # ── Compose dashboard ─────────────────────────────────────────────

    t3_dashboard = t3_legend | (

        t3_activity_chart | t3_popularity_chart | t3_influence_chart

    )


    mo.vstack([

        mo.ui.altair_chart(t3_dashboard),

        mo.callout(mo.md(

            "**Sailor Shift does not appear on the influence chart** — "

            "she has no incoming influence edges in the dataset, meaning no other "

            "work directly references hers via sampling, cover or style. "

            "Her impact is reflected instead in the OF community growth charts in Task 1c."

        ), kind='info')

    ])
    return


@app.cell
def _():
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Task 3b — Who is the next rising star in Oceanus Folk?
    We focus on recent years (2030+) and rank artists by three dimensions:
    activity (songs released), popularity (notable songs), and influence (works referencing theirs).
    We then compute a growth score — recent activity minus older activity — to find
    who is genuinely accelerating rather than just historically prolific.
    """)
    return


@app.cell
def _(
    t3_artist_influence_yearly,
    t3_artist_notable_yearly,
    t3_artist_yearly,
    t3_oceanus_artists,
):
    # ── Recent activity (2030+) per artist ───────────────────────────

    # Sum all songs released from 2030 onwards per artist.

    t3_rising_activity = (

        t3_artist_yearly[t3_artist_yearly['release_year'] >= 2030]

        .groupby('artist_name', as_index=False)['songs_per_year']

        .sum()

        .sort_values('songs_per_year', ascending=False)

    )


    # ── Recent popularity ─────────────────────────────────────────────

    t3_rising_combined = t3_rising_activity.merge(

        t3_artist_notable_yearly[t3_artist_notable_yearly['release_year'] >= 2030]

        .groupby('artist_name', as_index=False)['notable_songs_per_year'].sum(),

        on='artist_name', how='left'

    )

    t3_rising_combined['notable_songs_per_year'] = (

        t3_rising_combined['notable_songs_per_year'].fillna(0)

    )


    # ── Recent influence ──────────────────────────────────────────────

    t3_rising_combined = t3_rising_combined.merge(

        t3_artist_influence_yearly[t3_artist_influence_yearly['song_release_year'] >= 2030]

        .groupby('artist_name', as_index=False)['influence_per_year'].sum(),

        on='artist_name', how='left'

    )

    t3_rising_combined['influence_per_year'] = (

        t3_rising_combined['influence_per_year'].fillna(0)

    )


    # ── Filter: OF artists with ≥1 notable song, plus key candidates ──

    # We always include Sailor Shift, Daniel O'Connell and Beatrice Albright

    # as reference points even if they don't meet the OF filter.

    t3_key_artists = {"Sailor Shift", "Daniel O'Connell", "Beatrice Albright"}


    t3_rising_filtered = t3_rising_combined[

        (

            t3_rising_combined['artist_name'].isin(t3_oceanus_artists) &

            (t3_rising_combined['notable_songs_per_year'] >= 1)

        ) |

        t3_rising_combined['artist_name'].isin(t3_key_artists)

    ].copy()


    # ── Growth score: recent (≥2035) minus older activity ─────────────

    # Positive = accelerating, negative = more prolific earlier in career.

    t3_growth = (

        t3_artist_yearly.copy()

        .assign(period=lambda df: df['release_year'].apply(

            lambda y: 'recent' if y >= 2035 else 'older'

        ))

        .groupby(['artist_name', 'period'])['songs_per_year']

        .sum()

        .unstack(fill_value=0)

        .reset_index()

    )

    t3_growth['growth_score'] = t3_growth['recent'] - t3_growth['older']


    # ── Final candidate table ─────────────────────────────────────────

    t3_focus_artists = [

        "Gang Zhu", "Chao Zheng", "Amber Smith", "Jie Su", "Min Tian", "Min Kong",

        "Sailor Shift", "Daniel O'Connell", "Beatrice Albright"

    ]


    t3_candidates = (

        t3_rising_filtered[t3_rising_filtered['artist_name'].isin(t3_focus_artists)]

        .merge(t3_growth[['artist_name', 'growth_score']], on='artist_name', how='left')

        .sort_values(['songs_per_year', 'notable_songs_per_year', 'influence_per_year'],

                     ascending=False)

    )


    print("Candidate artists:")

    print(t3_candidates[['artist_name', 'songs_per_year',

                          'notable_songs_per_year', 'influence_per_year', 'growth_score']])
    return t3_candidates, t3_rising_filtered


@app.cell
def _(alt, mo, t3_candidates, t3_rising_filtered):
    # ── Scatter: activity vs popularity (all OF rising artists) ──────

    # Each dot is one artist. Position shows recent activity (x)

    # vs recent popularity (y). Click to highlight.

    t3_scatter_selection = alt.selection_point(fields=['artist_name'])


    t3_scatter = alt.Chart(t3_rising_filtered).transform_calculate(

        jitter_x='datum.songs_per_year + (random() - 0.5) * 0.22',

        jitter_y='datum.notable_songs_per_year + (random() - 0.5) * 0.22'

    ).mark_circle(size=220).encode(

        x=alt.X('jitter_x:Q', title='Recent Activity (Songs Released 2030+)'),

        y=alt.Y('jitter_y:Q', title='Recent Popularity (Notable Songs 2030+)'),

        color=alt.Color('artist_name:N', legend=None),

        opacity=alt.condition(t3_scatter_selection, alt.value(1), alt.value(0.15)),

        tooltip=[

            alt.Tooltip('artist_name:N', title='Artist'),

            alt.Tooltip('songs_per_year:Q', title='Recent Activity'),

            alt.Tooltip('notable_songs_per_year:Q', title='Recent Popularity'),

        ]

    ).add_params(t3_scatter_selection).properties(

        title='Emerging Oceanus Folk Artists — Activity vs Popularity (2030+)',

        width=550, height=380

    )


    # ── Bar: growth score for final candidates ────────────────────────

    # Green = growing (positive score), orange = declining (negative score).

    t3_growth_bar = alt.Chart(t3_candidates).mark_bar().encode(

        x=alt.X('growth_score:Q', title='Growth Score (Recent − Older Activity)'),

        y=alt.Y('artist_name:N', sort='-x', title='Artist'),

        color=alt.condition(

            alt.datum.growth_score > 0,

            alt.value('#54a24b'),

            alt.value('#e07b39')

        ),

        tooltip=[

            alt.Tooltip('artist_name:N', title='Artist'),

            alt.Tooltip('growth_score:Q', title='Growth Score'),

            alt.Tooltip('songs_per_year:Q', title='Recent Activity'),

            alt.Tooltip('notable_songs_per_year:Q', title='Recent Popularity'),

            alt.Tooltip('influence_per_year:Q', title='Recent Influence'),

        ]

    ).properties(

        title='Growth Score of Final Candidates (2035+ vs Earlier)',

        width=580, height=320

    )


    mo.vstack([

        mo.ui.altair_chart(t3_scatter),

        mo.ui.altair_chart(t3_growth_bar),

        mo.callout(mo.md(

            "All candidates show **negative growth scores**, meaning they were more active "

            "earlier in their careers than in the most recent period. "

            "Daniel O'Connell and Beatrice Albright stand out on both activity and popularity. "

            "The growth bar helps distinguish whether recent output is accelerating or tapering."

        ), kind='info')

    ])
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
