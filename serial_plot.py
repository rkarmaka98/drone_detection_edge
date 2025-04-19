import pandas as pd
import gradio as gr
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import matplotlib.dates as mdates

# Global variable to store the DataFrame
global_df = None
CSV_PATH = "/media/tony/434E-9EF5/detections.csv"  # Update this path

def load_data(csv_path):
    """Load and return the CSV data, or None if failed"""
    try:
        df = pd.read_csv(csv_path)
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return None

def generate_plots(df, min_confidence=0.0, selected_class="All"):
    if df is None or df.empty:
        return None
    
    filtered_df = df[df['score'] >= min_confidence]
    if selected_class != "All":
        filtered_df = filtered_df[filtered_df['class'] == selected_class]
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    
    # Plot 1: Confidence over time (improved time formatting)
    ax1.scatter(filtered_df['datetime'], filtered_df['score'], alpha=0.5, s=10)
    ax1.set_title('Confidence Over Time')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Confidence Score')
    ax1.grid(True)
    
    # Format x-axis to show HH:MM:SS
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    fig.autofmt_xdate(rotation=45)
    
    # Plot 2: Position heatmap
    hb = ax2.hexbin(
        filtered_df['x'], 
        filtered_df['y'], 
        gridsize=15, 
        cmap='inferno', 
        extent=(0, 320, 0, 240)
    )
    ax2.invert_yaxis()
    fig.colorbar(hb, ax=ax2, label='Detection Count')
    ax2.set_title('Position Heatmap')
    ax2.set_xlabel('X Position')
    ax2.set_ylabel('Y Position')
    
    # Plot 3: Detection frequency (improved time bin formatting)
    if not filtered_df.empty:
        time_bins = pd.cut(filtered_df['datetime'], bins=min(20, len(filtered_df)))
        bin_counts = filtered_df.groupby(time_bins).size()
        
        # Format bin labels as HH:MM:SS
        bin_labels = [
            f"{x.left.strftime('%H:%M:%S')}\nto\n{x.right.strftime('%H:%M:%S')}" 
            for x in bin_counts.index
        ]
        
        ax3.bar(bin_labels, bin_counts.values)
        ax3.set_title('Detection Frequency')
        ax3.set_xlabel('Time Bins')
        ax3.set_ylabel('Count')
        ax3.tick_params(axis='x', which='major', labelsize=8)
    
    # Plot 4: Confidence distribution
    ax4.hist(filtered_df['score'], bins=20, edgecolor='black')
    ax4.set_title('Confidence Distribution')
    ax4.set_xlabel('Confidence Score')
    ax4.set_ylabel('Count')
    
    plt.tight_layout()
    return fig

def update_plots(min_confidence, selected_class):
    return generate_plots(global_df, min_confidence, selected_class)

def reload_data():
    global global_df
    global_df = load_data(CSV_PATH)
    if global_df is not None:
        classes = ["All"] + sorted(global_df['class'].unique().tolist())
        return (
            classes,  # Updated dropdown choices
            "All",    # Reset dropdown value
            generate_plots(global_df, 0.3, "All"),  # Updated plot
            global_df.head(100)  # Updated raw data
        )
    else:
        raise gr.Error("Failed to reload CSV file!")

with gr.Blocks(title="Drone Detection Dashboard") as app:
    gr.Markdown("# 🚁 OpenMV Drone Detection Dashboard")
    
    # Load data initially
    global_df = load_data(CSV_PATH)
    initial_classes = ["All"] + sorted(global_df['class'].unique().tolist()) if global_df is not None else ["All"]
    
    # Controls
    with gr.Row():
        min_confidence = gr.Slider(0, 1, value=0.3, label="Min Confidence")
        selected_class = gr.Dropdown(initial_classes, value="All", label="Filter by Class")
        reload_btn = gr.Button("🔄 Reload Data", variant="secondary")
    
    # Outputs
    plot_output = gr.Plot()
    raw_data = gr.Dataframe(
        value=global_df.head(100) if global_df is not None else None, 
        label="Raw Data (First 100 Rows)", 
        interactive=False
    )
    
    # Event handlers
    min_confidence.change(
        update_plots, 
        inputs=[min_confidence, selected_class], 
        outputs=plot_output
    )
    selected_class.change(
        update_plots, 
        inputs=[min_confidence, selected_class], 
        outputs=plot_output
    )
    reload_btn.click(
        reload_data,
        outputs=[selected_class, selected_class, plot_output, raw_data]
    )

if __name__ == "__main__":
    app.launch(share=False)