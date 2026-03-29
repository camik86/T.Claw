import json
import os
import logging
from openai import OpenAI
from config import config
from tools import TOOLS, FUNCTION_MAP

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


SYSTEM_PROMPT_TEMPLATE = """你是 T.Claw，一个桌面控制助手。你可以控制用户的电脑执行各种操作。

【核心原则】
你必须完全模拟人类的操作方式，实时掌控鼠标：
- 所有操作都通过鼠标移动、点击、键盘输入完成
- 像人类一样：动一下鼠标，看一下屏幕，确认位置正确再继续
- 禁止使用任何系统命令、API 调用、脚本执行
- 创建文件：右键菜单 → 新建 → 文本文档 →
- 重命名文件：右键文件 → 显示更多选项 → 重命名(M)
- 打开软件：鼠标移动到图标位置 → 双击

【实时掌控鼠标 - 最重要原则！】
你必须像人类一样实时掌控鼠标：
1. 每次移动鼠标前：先截图确认当前鼠标位置
2. 每次移动鼠标后：立即截图确认鼠标到达了正确位置
3. 每次点击前：先截图确认鼠标在正确的目标上
4. 每次操作后：立即验证结果
- 模拟人类"动一下看一下"的掌控方式
- 绝不允许在没确认位置的情况下连续操作
- 截图确认是每次操作的必要前提！

【操作能力】
- 平滑移动鼠标（duration 参数控制速度）
- 鼠标点击（左键/右键/双击）
- 鼠标滚轮、拖拽
- 键盘输入文字（可设置打字间隔）
- 组合键、单按键
- 两级截图系统查看屏幕状态

【两级截图系统 - 重要！】
我们使用两级定位方式：

1. **概览图 (screenshot_overview)**
   - 全屏截图，每200像素一个蓝色网格
   - 纵轴用 A-Z 标注（A=第0行，B=第1行，C=第2行...）
   - 横轴用数字标注（0=第0列，1=第1列，2=第2列...）
   - 用于：粗略定位目标所在的区域（如 C12 表示第2行第12列）

2. **详细图 (screenshot_detail)**
   - 截取3x3块矩阵（共9个块），所有块都放大4倍
   - 中心块为目标区域，带20像素红色网格
   - 每个网格交叉点标注绝对坐标（黄色文字）
   - 周围8个邻近块只显示块编号
   - 用于：精确定位目标坐标

【工作流程 - 单步执行模式】
**重要：每次只执行一个操作，完成后截图确认，再规划下一步！**

标准流程：
1. 截图查看当前状态
2. 决定下一步操作（只规划一步）
3. 执行这一步操作
4. 截图确认操作结果
5. 根据结果决定是否继续或调整

**禁止：** 一开始就规划所有操作步骤
**要求：** 每次只做一步，确认后再做下一步

示例流程：
→ screenshot_overview()  // 第一步：看全屏
→ （分析：目标在C5块）
→ screenshot_detail("C5")  // 第二步：看详细
→ （分析：目标在1050,430）
→ mouse_move(1050, 430)  // 第三步：移动
→ screenshot_overview()  // 第四步：确认位置
→ （分析：位置正确）
→ mouse_click()  // 第五步：点击
→ screenshot_overview()  // 第六步：确认结果

【重要提醒】
- 绝对不能在没有查看详细截图的情况下直接移动鼠标！
- 每次 mouse_move 前必须先 screenshot_detail 查看目标区域的详细坐标！

【坐标系规则】
- X 轴 = 水平位置（从左到右，左边是 0）
- Y 轴 = 垂直位置（从上到下，上面是 0）
- 屏幕左上角是 (0, 0)
- 每个分块对应：X = 列数 × 200，Y = 行数 × 200

【分块标签解析】
- 分块标签格式：字母 + 数字，如 C5、A3、Z20
- 字母部分：表示行（A=0, B=1, C=2...）
- 数字部分：表示列（0, 1, 2...）
- 例如：C5 = 第2行第5列 = Y=400, X=1000（起点坐标）

【相对位移概念】
- 往上移动 = Y 坐标减小
- 往下移动 = Y 坐标增大
- 往左移动 = X 坐标减小
- 往右移动 = X 坐标增大
- 小幅移动：50-100 像素
- 中等移动：150-250 像素
- 大幅移动：300-500 像素

【Few-shot 示例 - 单步执行模式】
示例 1：点击文件图标（每次只做一步）
→ screenshot_overview()  // 步骤1：看全屏
→ （分析：目标在C5块，现在需要看详细图）
→ screenshot_detail("C5")  // 步骤2：看详细
→ （分析：目标在1050,430，现在需要移动鼠标）
→ mouse_move(1050, 430)  // 步骤3：移动
→ screenshot_overview()  // 步骤4：确认位置
→ （分析：位置正确，现在可以点击）
→ mouse_click()  // 步骤5：点击

示例 2：从 (500, 500) 往右小幅移动（单步操作）
→ mouse_move(580, 500)
→ screenshot_overview()  // 确认位置

示例 3：点击桌面图标（完整单步流程）
→ screenshot_overview()  // 步骤1：看全屏
→ （分析：图标在D0块）
→ screenshot_detail("D0")  // 步骤2：看详细
→ （分析：图标在120,620）
→ mouse_move(120, 620)  // 步骤3：移动
→ screenshot_overview()  // 步骤4：确认
→ （分析：位置正确）
→ mouse_click()  // 步骤5：点击



【操作原则 - 必须严格遵守！】
1. 【截图确认】任何鼠标操作前（mouse_move、mouse_click、mouse_drag等），必须先截图确认当前鼠标位置
2. 【定位流程】先用 screenshot_overview() 确认屏幕状态，再用 screenshot_detail() 查看目标区域详细坐标
3. 【精确移动】根据详细截图的精确坐标移动鼠标，绝不能估算坐标
4. 【移动确认】mouse_move 后立即 screenshot_overview() 确认到达位置
5. 【点击确认】mouse_click 前截图确认鼠标在正确目标上，点击后再截图确认结果
6. 【错误恢复】遇到错误时，重新截图分析原因并重试
7. 【安全第一】不要执行危险操作（如删除系统文件）

【实时掌控模式 - 强制执行】
每次操作的标准模式：
1. 截图确认当前位置
2. 分析目标位置
3. 计算移动距离
4. 执行移动
5. 截图确认到达位置
6. 执行操作
7. 截图确认结果

【重要要求】
1. **单步执行模式：每次只执行一个操作，完成后截图确认，再决定下一步**
2. 必须使用工具调用来执行所有操作，不要直接用文字回复操作步骤
3. 只有在所有操作都完成后，才能用文字回复用户
4. 操作未完成时，不要说"完成"、"好了"等话语
5. 不确定屏幕状态时，先截图查看，再决定下一步操作
6. 定位时优先使用两级截图流程
7. **实时掌控：每次鼠标操作前、操作后都要截图确认位置！**
8. **像人类一样：动一下看一下，绝不允许盲目操作！**
9. **禁止一开始就规划所有步骤，必须一步步执行和确认**

当前屏幕分辨率：{screen_size}
桌面路径：{desktop_path}
"""


class Agent:
    def __init__(self):
        self.client = None
        self.messages = []
        self._init_client()

    def _init_client(self):
        if config.api_key:
            self.client = OpenAI(
                api_key=config.api_key,
                base_url="https://ark.cn-beijing.volces.com/api/v3"
            )
            self._reset_messages()

    def _reset_messages(self):
        screen_size = config.screen_size
        desktop_path = config.desktop_path
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            screen_size=screen_size,
            desktop_path=desktop_path
        )
        self.messages = [{"role": "system", "content": system_prompt}]

    def is_configured(self):
        return bool(config.api_key)

    def update_config(self):
        self._init_client()

    def chat(self, user_input, stream=False):
        if not self.is_configured():
            return "请先在设置页面配置 API Key"

        logger.info(f"📥 用户输入: {user_input}")
        self.messages.append({"role": "user", "content": user_input})
        
        max_iterations = 40
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            logger.info(f"🔄 第 {iteration} 轮对话")
            
            response = self.client.chat.completions.create(
                model=config.model,
                messages=self.messages,
                tools=TOOLS,
                tool_choice="auto",
                stream=stream,
                stream_options={"include_usage": True} if stream else None
            )

            if stream:
                message = self._handle_stream_response(response)
            else:
                message = response.choices[0].message
            
            self.messages.append(message)

            if not message.tool_calls:
                if iteration < max_iterations:
                    logger.info(f"✅ 任务完成")
                    return message.content or "任务执行完成"
                else:
                    logger.info(f"⚠️ 达到最大迭代次数")
                    return "任务执行中，但由于达到最大迭代次数，已暂停"

            tool_results = []
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                try:
                    args = json.loads(tool_call.function.arguments)
                except:
                    args = {}
                
                cleaned_args = {}
                for key, value in args.items():
                    if key and key.strip() and key not in ['parameters', 'parameter']:
                        cleaned_args[key] = value
                args = cleaned_args

                logger.info(f"🔧 调用工具: {func_name}({args})")
                
                if func_name in FUNCTION_MAP:
                    result = FUNCTION_MAP[func_name](**args)
                else:
                    result = f"未知函数：{func_name}"

                if func_name in ["screenshot", "screenshot_overview", "screenshot_detail"] and isinstance(result, str):
                    logger.info(f"📸 截图完成 (base64 长度: {len(result)})")
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": [
                            {"type": "text", "text": "当前屏幕截图："},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{result}"
                                }
                            }
                        ]
                    })
                else:
                    logger.info(f"📤 工具返回: {result}")
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result)
                    })
            
            for tool_result in tool_results:
                self.messages.append(tool_result)

    def _handle_stream_response(self, stream):
        from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageToolCall
        from openai.types.chat.chat_completion_message_tool_call import Function
        
        content = ""
        tool_calls = []
        current_tool_call = None
        
        for chunk in stream:
            if chunk.choices:
                delta = chunk.choices[0].delta
                
                if delta.content:
                    content += delta.content
                
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        if current_tool_call is None:
                            current_tool_call = {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name if tc.function else "",
                                    "arguments": ""
                                }
                            }
                        if tc.function and tc.function.arguments:
                            current_tool_call["function"]["arguments"] += tc.function.arguments
                
                if chunk.choices[0].finish_reason == "tool_calls":
                    if current_tool_call:
                        tool_calls.append(ChatCompletionMessageToolCall(
                            id=current_tool_call["id"],
                            type="function",
                            function=Function(
                                name=current_tool_call["function"]["name"],
                                arguments=current_tool_call["function"]["arguments"]
                            )
                        ))
                    break
        
        return ChatCompletionMessage(
            role="assistant",
            content=content,
            tool_calls=tool_calls if tool_calls else None
        )


agent = Agent()
