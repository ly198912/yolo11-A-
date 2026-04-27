import cv2
import os


def extract_frames(video_path, output_folder, interval_seconds=1):
    # 1. 创建输出目录
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 2. 读取视频文件
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("错误：无法打开视频文件。")
        return

    # 3. 获取视频的帧率 (FPS)
    fps = cap.get(cv2.CAP_PROP_FPS)
    # 计算每隔多少帧提取一次 (例如 30fps * 2s = 60帧)
    frame_interval = int(fps * interval_seconds)

    frame_count = 0
    saved_count = 0

    print(f"视频帧率: {fps}, 将每隔 {frame_interval} 帧（即 {interval_seconds} 秒）保存一次。")

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # 视频读取完毕

        # 4. 判断是否到了抽帧点
        if frame_count % frame_interval == 0:
            save_path = os.path.join(output_folder, f"frame_{saved_count:04d}.jpg")
            cv2.imwrite(save_path, frame)
            print(f"已保存: {save_path}")
            saved_count += 1

        frame_count += 1

    cap.release()
    print(f"抽帧完成！共保存 {saved_count} 张图片。")


# --- 使用示例 ---
extract_frames(r"D:\yolo\yolo11\dnf\snd.mp4", "extracted_images", interval_seconds=2)