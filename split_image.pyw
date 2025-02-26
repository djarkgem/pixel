from PIL import Image
import os
import tkinter as tk
from tkinter import filedialog

def split_image(input_path, output_folder):
    """이미지를 왼쪽부터 9:16 비율로 여러 장 잘라 저장하는 함수"""
    os.makedirs(output_folder, exist_ok=True)  # 출력 폴더 생성
    
    img = Image.open(input_path)
    img_width, img_height = img.size

    # 9:16 비율에 맞는 가로 크기 계산
    target_width = int(img_height * (9 / 16))

    # 자를 이미지 개수 계산
    num_slices = img_width // target_width

    for i in range(num_slices):
        left = i * target_width
        right = left + target_width
        if right > img_width:  # 마지막 부분이 부족하면 종료
            break
        
        cropped = img.crop((left, 0, right, img_height))
        output_path = os.path.join(output_folder, f"slice_{i+1}.png")
        cropped.save(output_path)
        print(f"저장 완료: {output_path}")

    print(f"총 {num_slices}개의 이미지가 저장되었습니다.")

def select_image():
    """파일 선택 다이얼로그로 이미지 선택 후 split_image 실행"""
    root = tk.Tk()
    root.withdraw()  # Tk 창 숨기기

    file_path = filedialog.askopenfilename(
        title="긴 이미지를 선택하세요",
        filetypes=[("이미지 파일", "*.png;*.jpg;*.jpeg")]
    )

    if file_path:
        output_directory = "output"  # 자른 이미지 저장 폴더
        split_image(file_path, output_directory)
    else:
        print("파일을 선택하지 않았습니다.")

# 실행
select_image()
