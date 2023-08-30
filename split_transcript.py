from pydub import AudioSegment
from pydub.playback import play
from pydub.silence import split_on_silence
import re
import os

def srt_to_milliseconds(time_str):
    [h, m, s_ms] = re.split(':', time_str)
    [s, ms] = s_ms.split(',')
    print ([h, m,s, ms])
    return int(h) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(ms)

def split_audio(audio_path, srt_path, output_folder, transcript_folder):
    audio = AudioSegment.from_wav(audio_path)
    
    with open(srt_path, 'r') as srt_file:
        lines = srt_file.readlines()
        
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.isdigit():
            i += 1
            times = lines[i].strip().split(' --> ')
            start_time = srt_to_milliseconds(times[0])
            end_time = srt_to_milliseconds(times[1])
            
            segment = audio[start_time:end_time]
            output_index = int(line)
            audio_filename = os.path.splitext(os.path.basename(audio_path))[0]
            output_name = f"{audio_filename}_{output_index:03}.wav"
            output_path = os.path.join(output_folder, output_name)
            segment.export(output_path, format="wav")
            
            transcript = lines[i+1].strip()  # Lấy dòng phụ đề tương ứng
            transcript_filename = f"{output_name[:-4]}.txt"
            transcript_path = os.path.join(transcript_folder, transcript_filename)
            
            with open(transcript_path, 'w') as trs_file:
                trs_file.write(transcript)
        
        i += 1

if __name__ == "__main__":
    audio_path = "1.wav"
    srt_path = "1.srt"
    output_folder = "output_audio"
    transcript_folder = "output_trs"
    
    os.makedirs(transcript_folder, exist_ok=True)  # Tạo thư mục transcript nếu chưa có
    
    split_audio(audio_path, srt_path, output_folder, transcript_folder)