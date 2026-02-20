import gradio as gr

def hello(name):
    return f"ZeroGPU ready ✅ Hello, {name}!"

demo = gr.Interface(fn=hello, inputs=gr.Text(label="Name"), outputs=gr.Text(label="Output"), title="1001 IBL Video Avatar")
if __name__ == "__main__":
    demo.launch()
