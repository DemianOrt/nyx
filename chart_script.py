import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Data for the architecture components with consistent colors by type
data = [
    {"component": "Usuario/Cliente", "type": "External", "x": 1, "y": 6, "color": "#1FB8CD"},
    {"component": "Servidor Node.js", "type": "Server", "x": 3, "y": 6, "color": "#DB4545"},
    {"component": "Puente Python", "type": "Bridge", "x": 5, "y": 6, "color": "#2E8B57"},
    {"component": "Query Router", "type": "Router", "x": 7, "y": 6, "color": "#5D878F"},
    {"component": "Nivel 1: Clasificador Local", "type": "Routing Level", "x": 9, "y": 8.5, "color": "#D2BA4C"},
    {"component": "Nivel 2: Gemini API", "type": "Routing Level", "x": 9, "y": 6, "color": "#D2BA4C"},
    {"component": "Nivel 3: Perplexity API", "type": "Routing Level", "x": 9, "y": 3.5, "color": "#D2BA4C"},
    {"component": "Calendar Skill", "type": "Skill", "x": 11, "y": 7.5, "color": "#B4413C"},
    {"component": "Perplexity Skill", "type": "Skill", "x": 11, "y": 4.5, "color": "#B4413C"},
    {"component": "Google Calendar API", "type": "External API", "x": 13, "y": 8.5, "color": "#964325"},
    {"component": "Google Gemini API", "type": "External API", "x": 13, "y": 6, "color": "#964325"},
    {"component": "Perplexity API", "type": "External API", "x": 13, "y": 3.5, "color": "#964325"},
    {"component": "Budget Governor", "type": "Utility", "x": 11, "y": 2, "color": "#944454"}
]

df = pd.DataFrame(data)

# Create the figure
fig = go.Figure()

# Define connections between components
connections = [
    (1, 6, 3, 6),      # Usuario -> Servidor Node.js
    (3, 6, 5, 6),      # Servidor Node.js -> Puente Python
    (5, 6, 7, 6),      # Puente Python -> Query Router
    (7, 6, 9, 8.5),    # Query Router -> Nivel 1
    (7, 6, 9, 6),      # Query Router -> Nivel 2
    (7, 6, 9, 3.5),    # Query Router -> Nivel 3
    (9, 8.5, 11, 7.5), # Nivel 1 -> Calendar Skill
    (9, 6, 11, 7.5),   # Nivel 2 -> Calendar Skill  
    (9, 3.5, 11, 4.5), # Nivel 3 -> Perplexity Skill
    (11, 7.5, 13, 8.5), # Calendar Skill -> Google Calendar API
    (9, 6, 13, 6),      # Nivel 2 -> Google Gemini API
    (11, 4.5, 13, 3.5), # Perplexity Skill -> Perplexity API
    (7, 6, 11, 2)       # Query Router -> Budget Governor
]

# Add connection lines with arrows
for i, (x1, y1, x2, y2) in enumerate(connections):
    # Add the line
    fig.add_trace(go.Scatter(
        x=[x1, x2], y=[y1, y2],
        mode='lines',
        line=dict(color='#666666', width=2),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Calculate arrow position and direction
    dx = x2 - x1
    dy = y2 - y1
    length = np.sqrt(dx**2 + dy**2)
    
    # Normalize and create arrow
    if length > 0:
        # Position arrow at 75% of the line length to avoid text overlap
        arrow_x = x1 + 0.75 * dx
        arrow_y = y1 + 0.75 * dy
        
        # Arrow direction (normalized)
        arrow_dx = dx / length
        arrow_dy = dy / length
        
        # Create arrowhead
        fig.add_annotation(
            x=arrow_x,
            y=arrow_y,
            ax=arrow_x - 0.1 * arrow_dx,
            ay=arrow_y - 0.1 * arrow_dy,
            xref='x', yref='y',
            axref='x', ayref='y',
            arrowhead=2,
            arrowsize=1.2,
            arrowwidth=2,
            arrowcolor='#666666',
            showarrow=True,
            text="",
        )

# Get unique component types and their colors
type_colors = df.groupby('type')['color'].first().to_dict()

# Add components as scatter points with consistent colors and better text
for component_type in df['type'].unique():
    type_data = df[df['type'] == component_type]
    
    # Abbreviate component names to fit character limit
    abbreviated_names = []
    for name in type_data['component']:
        if 'Clasificador' in name:
            abbreviated_names.append('Level 1')
        elif 'Google Calendar' in name:
            abbreviated_names.append('Google Cal')
        elif 'Google Gemini' in name:
            abbreviated_names.append('Gemini')
        elif 'Budget Governor' in name:
            abbreviated_names.append('Budget Gov')
        elif 'Usuario/Cliente' in name:
            abbreviated_names.append('Client')
        elif 'Servidor Node.js' in name:
            abbreviated_names.append('Node.js')
        elif 'Puente Python' in name:
            abbreviated_names.append('Python')
        elif 'Query Router' in name:
            abbreviated_names.append('Router')
        elif 'Calendar Skill' in name:
            abbreviated_names.append('Calendar')
        elif 'Perplexity Skill' in name:
            abbreviated_names.append('Perplexity')
        elif 'Perplexity API' in name and 'Nivel' not in name:
            abbreviated_names.append('Perplexity')
        elif 'Nivel 2' in name:
            abbreviated_names.append('Level 2')
        elif 'Nivel 3' in name:
            abbreviated_names.append('Level 3')
        else:
            abbreviated_names.append(name[:10])
    
    fig.add_trace(go.Scatter(
        x=type_data['x'],
        y=type_data['y'],
        mode='markers+text',
        marker=dict(
            size=45,
            color=type_colors[component_type],
            line=dict(width=3, color='white')
        ),
        text=abbreviated_names,
        textposition='middle center',
        textfont=dict(size=12, color='white', family='Arial Black'),
        name=component_type,
        hovertemplate='<b>%{text}</b><br>Type: ' + component_type + '<extra></extra>'
    ))

# Update layout with better spacing
fig.update_layout(
    title='Nyx AI Architecture',
    xaxis=dict(
        showgrid=False,
        showticklabels=False,
        zeroline=False,
        range=[0, 14]
    ),
    yaxis=dict(
        showgrid=False,
        showticklabels=False,
        zeroline=False,
        range=[1, 10]
    ),
    plot_bgcolor='white',
    legend=dict(
        orientation='h',
        yanchor='bottom',
        y=1.05,
        xanchor='center',
        x=0.5
    )
)

fig.update_traces(cliponaxis=False)

# Save the chart
fig.write_image('nyx_architecture_diagram.png', width=1200, height=800)
print("Final architecture diagram saved as nyx_architecture_diagram.png")