from pydub import AudioSegment
import os

def split_audio_and_create_transcripts(audio_path, transcript_path, output_dir):
    # Load audio file
    audio = AudioSegment.from_file(audio_path)
    
    # Đọc nội dung của file transcript
    with open(transcript_path, 'r') as f:
        transcript_lines = f.readlines()
    
    # Loops qua từng đoạn phụ trong transcript
    for i, line in enumerate(transcript_lines):
        # Tách thời gian bắt đầu và kết thúc từ đoạn phụ trong transcript
        start_time = line.split(' --> ')[0]
        end_time = line.split(' --> ')[1]
        
        # Chuyển đổi thời gian thành miliseconds
        start_ms = (int(start_time.split(':')[0]) * 3600 + int(start_time.split(':')[1]) * 60 + float(start_time.split(':')[2].replace(',', '.'))) * 1000
        end_ms = (int(end_time.split(':')[0]) * 3600 + int(end_time.split(':')[1]) * 60 + float(end_time.split(':')[2].replace(',', '.'))) * 1000
        
        # Cắt đoạn audio
        audio_segment = audio[start_ms:end_ms]
        
        # Lưu đoạn audio cắt ra
        output_audio_path = os.path.join(output_dir, f'audio_{i}.wav')
        audio_segment.export(output_audio_path, format='wav')
        
        # Lưu đoạn transcript vào file txt
        output_transcript_path = os.path.join(output_dir, f'transcript_{i}.txt')
        with open(output_transcript_path, 'w') as f:
            f.write(line)
            
# Đường dẫn tới file audio và transcript
audio_path = 'tee_reduced_noise.wav'
transcript_path = 'path_to_your_transcript.txt'

# Thư mục lưu các mẩu nhỏ và file transcript tương ứng
output_dir = 'output_folder'

# Tạo thư mục nếu chưa tồn tại
os.makedirs(output_dir, exist_ok=True)

# Gọi hàm để cắt đoạn audio và tạo các file transcript tương ứng
split_audio_and_create_transcripts(audio_path, transcript_path, output_dir)