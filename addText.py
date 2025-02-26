import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont
import re

# 기본 폰트 경로 (한자가 포함된 경우 한자에만 사용)
DEFAULT_FONT_PATH = "arialuni.ttf"  # Windows에서 한자 지원되는 Arial Unicode MS 폰트
if not os.path.exists(DEFAULT_FONT_PATH):
    DEFAULT_FONT_PATH = "malgun.ttf"  # 대체 폰트 (Windows 기본 한글 폰트)

# 사용자 지정 폰트 경로 (MaruBuri-Regular.ttf)
FONT_PATH = os.path.join(os.path.dirname(__file__), "MaruBuri-Regular.ttf")

def select_images():
    """이미지 파일 선택"""
    return filedialog.askopenfilenames(title="이미지 파일 선택",
                                       filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])

def select_text_file():
    """텍스트 파일 선택"""
    return filedialog.askopenfilename(title="텍스트 파일 선택",
                                      filetypes=[("Text Files", "*.txt")])

def split_text_by_script(text):
    """한자와 한글을 분리하여 리스트로 반환"""
    segments = []
    current_segment = ""
    current_is_chinese = None

    for char in text:
        is_chinese = bool(re.match(r'[\u4e00-\u9fff]', char))

        if current_is_chinese is None:
            current_is_chinese = is_chinese

        if is_chinese == current_is_chinese:
            current_segment += char
        else:
            segments.append((current_segment, current_is_chinese))
            current_segment = char
            current_is_chinese = is_chinese

    if current_segment:
        segments.append((current_segment, current_is_chinese))

    return segments

def wrap_text(draw, text, font, max_width):
    """주어진 너비를 초과하지 않도록 텍스트를 줄바꿈"""
    lines = []
    words = text.split()
    while words:
        line = words.pop(0)
        while words and draw.textbbox((0, 0), line + " " + words[0], font=font)[2] <= max_width:
            line += " " + words.pop(0)
        lines.append(line)
    return lines

def add_text_to_images(image_paths, text_lines, output_folder):
    """각 이미지에 텍스트 추가 후 저장"""
    os.makedirs(output_folder, exist_ok=True)

    for i, img_path in enumerate(image_paths):
        if i >= len(text_lines):
            break  # 텍스트가 이미지 개수보다 적으면 중단

        image = Image.open(img_path).convert("RGBA")  # RGBA 모드로 변환
        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))  # 투명한 레이어 생성
        draw = ImageDraw.Draw(overlay)

        # 글꼴 크기 조정 (기존 대비 20% 줄임)
        max_width = image.width * 0.9  # 텍스트는 전체 너비의 90% 이내
        font_size = int(image.height * 0.04)  # 기존 5% → 4%로 줄임

        # 기본 폰트 설정
        font_main = ImageFont.truetype(FONT_PATH, font_size)  # 한글/영어용
        font_chinese = ImageFont.truetype(DEFAULT_FONT_PATH, font_size)  # 한자용

        # 텍스트 줄바꿈 적용
        wrapped_text = wrap_text(draw, text_lines[i], font_main, max_width)

        # 줄 간격 추가
        line_spacing = font_size // 4  # 줄 간격 설정 (폰트 크기의 1/4)
        
        # 텍스트 박스 크기 정확하게 계산
        text_heights = [draw.textbbox((0, 0), line, font=font_main)[3] - draw.textbbox((0, 0), line, font=font_main)[1] for line in wrapped_text]
        text_height = sum(text_heights) + (len(text_heights) - 1) * line_spacing

        box_height = text_height + 20  # 상하 여백 추가
        box_y = (image.height - box_height) // 2  # 중앙 정렬

        # 반투명 검정 배경 박스 추가 (80% 투명도 적용)
        box = (0, box_y, image.width, box_y + box_height)
        draw.rectangle(box, fill=(0, 0, 0, 204))  # 80% 투명 검정 박스

        # 텍스트 그리기
        y = box_y + 10
        for line in wrapped_text:
            x = (image.width - draw.textbbox((0, 0), line, font=font_main)[2]) // 2  # 가운데 정렬
            segments = split_text_by_script(line)  # 한자와 한글을 분리

            for segment, is_chinese in segments:
                font = font_chinese if is_chinese else font_main
                draw.text((x, y), segment, font=font, fill="white")
                x += draw.textbbox((0, 0), segment, font=font)[2]  # 다음 글자 위치 이동

            y += text_heights[wrapped_text.index(line)] + line_spacing  # 줄 간격 포함하여 이동

        # 기존 이미지와 투명 레이어 병합
        combined = Image.alpha_composite(image, overlay)

        # 새 이미지 저장 (PNG로 저장해야 투명도 유지됨)
        output_path = os.path.join(output_folder, f"output_{i+1}.png")
        combined.save(output_path, format="PNG")

    messagebox.showinfo("완료", f"✅ 모든 이미지가 '{output_folder}' 폴더에 저장되었습니다!")

# GUI 창 숨기기
root = tk.Tk()
root.withdraw()

# 파일 선택
image_paths = select_images()
if not image_paths:
    messagebox.showerror("오류", "이미지를 선택하지 않았습니다.")
    root.destroy()  # 프로그램 종료
    exit()

text_file_path = select_text_file()
if not text_file_path:
    messagebox.showerror("오류", "텍스트 파일을 선택하지 않았습니다.")
    root.destroy()  # 프로그램 종료
    exit()

# 텍스트 읽기
with open(text_file_path, "r", encoding="utf-8") as f:
    text_lines = [line.strip() for line in f.readlines() if line.strip()]

if len(text_lines) < len(image_paths):
    messagebox.showwarning("경고", "텍스트 줄 수가 이미지 개수보다 적습니다. 일부 이미지는 텍스트 없이 저장됩니다.")

# 결과 저장 폴더
output_folder = "output_images"

# 이미지 처리 및 저장
add_text_to_images(image_paths, text_lines, output_folder)

# 프로그램 종료 (tkinter 프로세스 종료)
root.destroy()
