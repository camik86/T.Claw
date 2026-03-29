import pyautogui
import pyperclip
import time
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


def mouse_move(x, y, duration=0.3, incremental=True):
    if incremental:
        current_x, current_y = pyautogui.position()
        dx = x - current_x
        dy = y - current_y
        distance = (dx**2 + dy**2)**0.5
        
        max_step = 300
        if distance > max_step:
            steps = int(distance / max_step) + 1
            for i in range(1, steps + 1):
                step_x = current_x + dx * i / steps
                step_y = current_y + dy * i / steps
                pyautogui.moveTo(step_x, step_y, duration=duration/steps)
            return f"鼠标增量式移动到 ({x}, {y})，分 {steps} 步"
    
    pyautogui.moveTo(x, y, duration=duration)
    return f"鼠标移动到 ({x}, {y})"


def mouse_click(button="left", clicks=1):
    pyautogui.click(button=button, clicks=clicks)
    return f"鼠标{button}键点击{clicks}次"


def mouse_scroll(clicks):
    pyautogui.scroll(clicks)
    return f"鼠标滚轮滚动 {clicks} 次"


def mouse_drag(x, y, duration=0.3):
    pyautogui.dragTo(x, y, duration=duration)
    return f"鼠标拖拽到 ({x}, {y})"


def keyboard_type(text, interval=0.03):
    pyautogui.typewrite(text, interval=interval)
    return f"输入文字：{text}"


def keyboard_hotkey(keys):
    pyautogui.hotkey(*keys)
    return f"按下组合键: {'+'.join(keys)}"


def keyboard_press(key):
    pyautogui.press(key)
    return f"按下按键: {key}"


def get_screen_size():
    size = pyautogui.size()
    return [size.width, size.height]


def get_mouse_position():
    pos = pyautogui.position()
    return [pos.x, pos.y]


def _draw_mouse_indicator(draw, mouse_pos, width, height, font_large, font_small):
    draw.ellipse(
        [mouse_pos.x - 20, mouse_pos.y - 20, mouse_pos.x + 20, mouse_pos.y + 20],
        outline=(0, 255, 0),
        width=5
    )
    draw.line(
        [(mouse_pos.x - 30, mouse_pos.y), (mouse_pos.x + 30, mouse_pos.y)],
        fill=(0, 255, 0),
        width=4
    )
    draw.line(
        [(mouse_pos.x, mouse_pos.y - 30), (mouse_pos.x, mouse_pos.y + 30)],
        fill=(0, 255, 0),
        width=4
    )
    
    coord_text = f"当前鼠标: X={mouse_pos.x}, Y={mouse_pos.y}"
    text_bbox = draw.textbbox((0, 0), coord_text, font=font_large)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    text_x = min(mouse_pos.x + 25, width - text_width - 15)
    text_y = max(mouse_pos.y - 30, 10)
    
    draw.rectangle(
        [text_x - 8, text_y - 5, text_x + text_width + 8, text_y + text_height + 5],
        fill=(0, 0, 0),
        outline=(0, 255, 0),
        width=3
    )
    draw.text((text_x, text_y), coord_text, fill=(0, 255, 0), font=font_large)


def screenshot_overview():
    import datetime
    
    img = pyautogui.screenshot()
    img = img.convert("RGB")
    draw = ImageDraw.Draw(img)
    
    width, height = img.size
    grid_step = 200
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 20)
        font_medium = ImageFont.truetype("arial.ttf", 16)
        font_small = ImageFont.truetype("arial.ttf", 10)
    except:
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        except:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
    
    for x in range(0, width + grid_step, grid_step):
        draw.line([(x, 0), (x, height)], fill=(100, 100, 255), width=2)
    
    for y in range(0, height + grid_step, grid_step):
        draw.line([(0, y), (width, y)], fill=(100, 100, 255), width=2)
    
    col = 0
    for x in range(0, width + grid_step, grid_step):
        label = str(col)
        text_bbox = draw.textbbox((0, 0), label, font=font_medium)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        
        draw.rectangle([x + 5, 5, x + 5 + text_w + 10, 5 + text_h + 10], fill=(0, 0, 100, 200))
        draw.text((x + 10, 8), label, fill=(255, 255, 0), font=font_medium)
        
        draw.rectangle([x + 5, height - 5 - text_h - 10, x + 5 + text_w + 10, height - 5], fill=(0, 0, 100, 200))
        draw.text((x + 10, height - 5 - text_h - 5), label, fill=(255, 255, 0), font=font_medium)
        col += 1
    
    row = 0
    for y in range(0, height + grid_step, grid_step):
        if row < len(letters):
            label = letters[row]
        else:
            label = str(row)
        
        text_bbox = draw.textbbox((0, 0), label, font=font_medium)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        
        draw.rectangle([5, y + 5, 5 + text_w + 10, y + 5 + text_h + 10], fill=(0, 0, 100, 200))
        draw.text((10, y + 8), label, fill=(255, 255, 0), font=font_medium)
        
        draw.rectangle([width - 5 - text_w - 10, y + 5, width - 5, y + 5 + text_h + 10], fill=(0, 0, 100, 200))
        draw.text((width - 5 - text_w - 5, y + 8), label, fill=(255, 255, 0), font=font_medium)
        row += 1
    
    col = 0
    for x in range(0, width, grid_step):
        row = 0
        for y in range(0, height, grid_step):
            if row < len(letters):
                row_label = letters[row]
            else:
                row_label = str(row)
            block_label = f"{row_label}{col}"
            
            text_bbox = draw.textbbox((0, 0), block_label, font=font_small)
            text_w = text_bbox[2] - text_bbox[0]
            text_h = text_bbox[3] - text_bbox[1]
            
            center_x = x + grid_step // 2
            center_y = y + grid_step // 2
            
            draw.rectangle(
                [center_x - text_w//2 - 4, center_y - text_h//2 - 4, 
                 center_x + text_w//2 + 4, center_y + text_h//2 + 4],
                fill=(0, 0, 80, 150)
            )
            draw.text(
                (center_x - text_w//2, center_y - text_h//2), 
                block_label, 
                fill=(200, 200, 255), 
                font=font_small
            )
            row += 1
        col += 1
    
    mouse_pos = pyautogui.position()
    _draw_mouse_indicator(draw, mouse_pos, width, height, font_large, font_small)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_overview_{timestamp}.jpg"
    img.save(filename, format="JPEG", quality=92)
    
    buffered = BytesIO()
    img.save(buffered, format="JPEG", quality=92)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str


def screenshot_detail(block_label):
    import datetime
    
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    scale = 4
    
    row_part = ""
    col_part = ""
    for i, c in enumerate(block_label):
        if c.isalpha():
            row_part += c
        else:
            col_part = block_label[i:]
            break
    
    if row_part in letters:
        center_row = letters.index(row_part)
    else:
        try:
            center_row = int(row_part)
        except:
            center_row = 0
    
    try:
        center_col = int(col_part)
    except:
        center_col = 0
    
    block_size = 200
    center_region_x = center_col * block_size
    center_region_y = center_row * block_size
    
    screen_width, screen_height = pyautogui.size()
    
    total_width = block_size * 3
    total_height = block_size * 3
    
    canvas_width = total_width * scale
    canvas_height = total_height * scale
    
    canvas = Image.new('RGB', (canvas_width, canvas_height), (50, 50, 50))
    
    for row_offset in range(-1, 2):
        for col_offset in range(-1, 2):
            current_row = center_row + row_offset
            current_col = center_col + col_offset
            
            current_region_x = current_col * block_size
            current_region_y = current_row * block_size
            
            actual_reg_x = max(0, min(current_region_x, screen_width - 1))
            actual_reg_y = max(0, min(current_region_y, screen_height - 1))
            actual_reg_w = min(block_size, screen_width - actual_reg_x)
            actual_reg_h = min(block_size, screen_height - actual_reg_y)
            
            if actual_reg_w <= 0 or actual_reg_h <= 0:
                continue
            
            region_img = pyautogui.screenshot(region=(actual_reg_x, actual_reg_y, actual_reg_w, actual_reg_h))
            region_img = region_img.convert("RGB")
            
            region_img = region_img.resize((block_size * scale, block_size * scale), Image.Resampling.LANCZOS)
            
            paste_x = (col_offset + 1) * block_size * scale
            paste_y = (row_offset + 1) * block_size * scale
            
            canvas.paste(region_img, (paste_x, paste_y))
            
            if current_row < len(letters):
                row_label = letters[current_row]
            else:
                row_label = str(current_row)
            block_id = f"{row_label}{current_col}"
            
            is_center = (row_offset == 0 and col_offset == 0)
            
            if is_center:
                draw = ImageDraw.Draw(canvas)
                try:
                    font_small = ImageFont.truetype("arial.ttf", 10)
                except:
                    try:
                        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
                    except:
                        font_small = ImageFont.load_default()
                
                grid_step = 20 * scale
                
                for x in range(0, block_size * scale + grid_step, grid_step):
                    draw.line([(paste_x + x, paste_y), (paste_x + x, paste_y + block_size * scale)], fill=(255, 100, 100), width=1)
                
                for y in range(0, block_size * scale + grid_step, grid_step):
                    draw.line([(paste_x, paste_y + y), (paste_x + block_size * scale, paste_y + y)], fill=(255, 100, 100), width=1)
                
                offset_x, offset_y = actual_reg_x, actual_reg_y
                
                for x in range(0, block_size * scale + grid_step, grid_step):
                    for y in range(0, block_size * scale + grid_step, grid_step):
                        abs_x = offset_x + (x // scale)
                        abs_y = offset_y + (y // scale)
                        draw.rectangle([paste_x + x + 1, paste_y + y + 1, paste_x + x + 50, paste_y + y + 14], fill=(0, 0, 0, 150))
                        draw.text((paste_x + x + 2, paste_y + y + 2), f"({abs_x},{abs_y})", fill=(255, 255, 0), font=font_small)
                
                mouse_pos = pyautogui.position()
                rel_x = (mouse_pos.x - offset_x) * scale
                rel_y = (mouse_pos.y - offset_y) * scale
                
                if 0 <= rel_x < block_size * scale and 0 <= rel_y < block_size * scale:
                    draw.ellipse(
                        [paste_x + rel_x - 20, paste_y + rel_y - 20, paste_x + rel_x + 20, paste_y + rel_y + 20],
                        outline=(0, 255, 0),
                        width=5
                    )
                    draw.line(
                        [(paste_x + rel_x - 30, paste_y + rel_y), (paste_x + rel_x + 30, paste_y + rel_y)],
                        fill=(0, 255, 0),
                        width=4
                    )
                    draw.line(
                        [(paste_x + rel_x, paste_y + rel_y - 30), (paste_x + rel_x, paste_y + rel_y + 30)],
                        fill=(0, 255, 0),
                        width=4
                    )
    
    draw = ImageDraw.Draw(canvas)
    try:
        font_block = ImageFont.truetype("arial.ttf", 14 * scale)
    except:
        try:
            font_block = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14 * scale)
        except:
            font_block = ImageFont.load_default()
    
    for row_offset in range(-1, 2):
        for col_offset in range(-1, 2):
            is_center = (row_offset == 0 and col_offset == 0)
            if is_center:
                continue
            
            current_row = center_row + row_offset
            current_col = center_col + col_offset
            
            if current_row < len(letters):
                row_label = letters[current_row]
            else:
                row_label = str(current_row)
            block_id = f"{row_label}{current_col}"
            
            paste_x = (col_offset + 1) * block_size * scale
            paste_y = (row_offset + 1) * block_size * scale
            
            text_bbox = draw.textbbox((0, 0), block_id, font=font_block)
            text_w = text_bbox[2] - text_bbox[0]
            text_h = text_bbox[3] - text_bbox[1]
            
            center_x = paste_x + block_size * scale // 2
            center_y = paste_y + block_size * scale // 2
            
            draw.rectangle(
                [center_x - text_w//2 - 6, center_y - text_h//2 - 6, center_x + text_w//2 + 6, center_y + text_h//2 + 6],
                fill=(0, 0, 80, 200)
            )
            draw.text(
                (center_x - text_w//2, center_y - text_h//2),
                block_id,
                fill=(200, 200, 255),
                font=font_block
            )
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_detail_{block_label}_{timestamp}.jpg"
    canvas.save(filename, format="JPEG", quality=92)
    
    buffered = BytesIO()
    canvas.save(buffered, format="JPEG", quality=92)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str


def screenshot(region=None, mode='overview'):
    if mode == 'overview':
        return screenshot_overview()
    elif mode == 'detail' and region:
        pass
    return screenshot_overview()


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "mouse_move",
            "description": "平滑移动鼠标到指定位置，模拟人类操作。支持增量式移动（超过300像素时分步移动）",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X坐标（像素），0-屏幕宽度"
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y坐标（像素），0-屏幕高度"
                    },
                    "duration": {
                        "type": "number",
                        "description": "移动耗时（秒），默认0.3秒"
                    },
                    "incremental": {
                        "type": "boolean",
                        "description": "是否使用增量式移动，默认true"
                    }
                },
                "required": ["x", "y"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mouse_click",
            "description": "鼠标点击（支持左键、右键、双击）",
            "parameters": {
                "type": "object",
                "properties": {
                    "button": {
                        "type": "string",
                        "enum": ["left", "right", "middle"],
                        "description": "left/right/middle，默认left"
                    },
                    "clicks": {
                        "type": "integer",
                        "description": "点击次数，1=单击，2=双击，默认1"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mouse_scroll",
            "description": "鼠标滚轮滚动",
            "parameters": {
                "type": "object",
                "properties": {
                    "clicks": {
                        "type": "integer",
                        "description": "滚动量，正数向上，负数向下"
                    }
                },
                "required": ["clicks"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mouse_drag",
            "description": "鼠标拖拽（从当前位置拖动到目标位置）",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "目标X坐标"
                    },
                    "y": {
                        "type": "integer",
                        "description": "目标Y坐标"
                    },
                    "duration": {
                        "type": "number",
                        "description": "拖动耗时（秒），默认0.5秒"
                    }
                },
                "required": ["x", "y"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "keyboard_type",
            "description": "输入文字（模拟键盘打字）",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "要输入的文字内容"
                    },
                    "interval": {
                        "type": "number",
                        "description": "每个字符间隔（秒），默认0.05秒，模拟人类打字"
                    }
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "keyboard_hotkey",
            "description": "按下组合键",
            "parameters": {
                "type": "object",
                "properties": {
                    "keys": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "按键列表，如['ctrl', 'c']、['ctrl', 'shift', 'n']"
                    }
                },
                "required": ["keys"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "keyboard_press",
            "description": "按下单个按键",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "按键名称，如enter、escape、tab、delete、f1-f12"
                    }
                },
                "required": ["key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_screen_size",
            "description": "获取当前屏幕分辨率，返回格式：[宽度, 高度]，单位为像素。例如 [1920, 1080]。",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_mouse_position",
            "description": "获取当前鼠标位置，返回格式：[X坐标, Y坐标]，单位为像素。原点(0,0)在屏幕左上角。",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "screenshot_overview",
            "description": "截取全屏概览图，不需要任何参数。截图特点：每200像素一个蓝色网格，纵轴用A-Z标注（ A=0行,B=1行,C=2行...），横轴用数字标注（0,1,2...列），每个方块中间显示编号（如A0、C12表示第2行第12列）。适合快速定位目标在屏幕的大致位置。",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "screenshot_detail",
            "description": "截取3x3块矩阵的详细视图，所有9个块都放大4倍显示。中心块为目标区域，带有20像素红色网格和每个网格交叉点的绝对坐标标注（黄色文字）。周围8个邻近块只显示块编号（如B4、D6等）。用于精确定位目标坐标。",
            "parameters": {
                "type": "object",
                "properties": {
                    "block_label": {
                        "type": "string",
                        "description": "目标分块标签，格式为'字母+数字'，例如：C5（第2行第5列）、A0（第0行第0列）、B3（第1行第3列）。该块将作为中心块，周围8个邻近块会自动包含在截图中。"
                    }
                },
                "required": ["block_label"]
            }
        }
    }
]

FUNCTION_MAP = {
    "mouse_move": mouse_move,
    "mouse_click": mouse_click,
    "mouse_scroll": mouse_scroll,
    "mouse_drag": mouse_drag,
    "keyboard_type": keyboard_type,
    "keyboard_hotkey": keyboard_hotkey,
    "keyboard_press": keyboard_press,
    "get_screen_size": get_screen_size,
    "get_mouse_position": get_mouse_position,
    "screenshot_overview": screenshot_overview,
    "screenshot_detail": screenshot_detail,
    "screenshot": screenshot_overview
}
