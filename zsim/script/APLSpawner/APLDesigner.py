import gradio as gr
from components.SortableRow import SortableRow


def create_next_step_interface():
    with gr.TabItem("下一步操作", id=1, visible=False) as tab:
        with gr.Column():
            gr.Markdown("## 动态横条配置")

            # 存储横条数据
            rows_state = gr.State(value=[])

            # 横条容器
            rows_container = gr.HTML()

            # 控制按钮
            with gr.Row():
                add_btn = gr.Button("➕ 添加新横条")
                save_btn = gr.Button("💾 保存配置")
            # 添加初始化横条
            initial_row = SortableRow(1, ["选项A", "选项B"])
            rows_container = initial_row.row

            def add_row(rows):
                new_id = len(rows) + 1
                new_row = SortableRow(new_id, ["选项A", "选项B"])
                return new_row.row

            add_btn.click(fn=add_row, inputs=rows_state, outputs=rows_container)

    return tab, add_btn, save_btn, rows_state, rows_container
