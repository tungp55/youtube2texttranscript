import youtube_dl
import os
from pytube import Playlist
from os import path
from pydub import AudioSegment

def download_ytvid_as_mp3(video_url, output_path):
    video_info = youtube_dl.YoutubeDL().extract_info(url=video_url, download=False)
    filename = f"{video_info['title']}.mp3"
    file_path = os.path.join(output_path, filename)

    options = {
        'format': 'bestaudio/best',
        'keepvideo': False,
        'outtmpl': file_path,
    }

    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([video_info['webpage_url']])

    print("Download complete... {}".format(filename))



def convert_mp3_to_wav(input_folder, output_folder):
    # Lặp qua tất cả các tập tin trong thư mục đầu vào
    for filename in os.listdir(input_folder):
        if filename.endswith(".mp3"):
            input_path = os.path.join(input_folder, filename)
            output_filename = os.path.splitext(filename)[0] + ".wav"
            output_path = os.path.join(output_folder, output_filename)
            print("intput path: "+ input_path)
            try:
                audio = AudioSegment.from_file(input_path)
            except:
                audio = AudioSegment.from_file(input_path, format="mp4")
            audio = audio.set_frame_rate(16000)
            audio = audio.set_channels(1)
            audio.export(output_path, format="wav")

    print("Chuyển đổi hoàn thành.")

def convert_mp3_to_wav_and_rename(input_folder, output_folder, csv_filename):
    # Lặp qua tất cả các tập tin trong thư mục đầu vào
    count = 1
    file_map = []  # Tạo một danh sách để lưu thông tin map giữa tên tệp mp3 và .wav
    for filename in os.listdir(input_folder):
        if filename.endswith(".mp3"):
            input_path = os.path.join(input_folder, filename)
            output_filename = f"{count}.wav"
            output_path = os.path.join(output_folder, output_filename)
            print(str(count), "Input path:", input_path)
            try:
                audio = AudioSegment.from_file(input_path)
            except:
                audio = AudioSegment.from_file(input_path, format="mp4")
            audio = audio.set_frame_rate(16000)
            audio = audio.set_channels(1)
            audio.export(output_path, format="wav")
            
            # Thêm thông tin map vào danh sách
            file_map.append((filename, output_filename))
            
            count += 1

    # Ghi thông tin map vào tệp CSV
    with open(csv_filename, "w", newline="", encoding="utf-8") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["MP3 Filename", "WAV Filename"])
        for mp3_filename, wav_filename in file_map:
            csv_writer.writerow([mp3_filename, wav_filename])

    print("Chuyển đổi hoàn thành và tạo file CSV.")

from scipy.io import wavfile
import noisereduce as nr
# load data
def reduce_noise_in_folder(input_folder, output_folder):
    # Lấy danh sách tên tệp trong thư mục đầu vào
    input_files = os.listdir(input_folder)

    # Duyệt qua từng tệp trong danh sách
    for filename in input_files:
        # Tạo đường dẫn đầy đủ cho tệp đầu vào
        input_path = os.path.join(input_folder, filename)
        
        # Tạo đường dẫn đầy đủ cho tệp đầu ra
        output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.wav")
        
        # Đọc dữ liệu âm thanh từ tệp đầu vào
        rate, data = wavfile.read(input_path)
        
        # Thực hiện khử tiếng ồn
        reduced_noise = nr.reduce_noise(y=data, sr=rate)
        
        # Ghi dữ liệu âm thanh đã xử lý vào tệp đầu ra
        wavfile.write(output_path, rate, reduced_noise)


# URL_PLAYLIST = "https://www.youtube.com/playlist?list=PLmStOnZvdb1LUHOkxdmD4DQ8IVmYo90jb"

# # Retrieve URLs of videos from playlist
# playlist = Playlist(URL_PLAYLIST)
# print('Number Of Videos In playlist: %s' % len(playlist.video_urls))

# urls = []
# for url in playlist:
#     download_ytvid_as_mp3(output_path="mp3_down", video_url=url)



# # Đường dẫn tới thư mục chứa các tập tin âm thanh ban đầu
# input_folder_path = "mp3_down"

# # Đường dẫn tới thư mục để lưu các tập tin âm thanh mới sau khi chuyển đổi
# output_folder_path = "wav_down"

# # Tên tệp CSV để lưu thông tin map
# csv_filename = "file_map.csv"

# # Gọi hàm để thực hiện chuyển đổi và lưu thông tin map vào tệp CSV
# convert_mp3_to_wav_and_rename(input_folder_path, output_folder_path, csv_filename)

# Bỏ âm thanh nền (optional)
# Đường dẫn thư mục chứa các tệp âm thanh cần xử lý
input_noise_folder = "wav_down"

# Đường dẫn thư mục để lưu các tệp sau khi đã xử lý
output_remove_noise_folder = "renoise_wavs"

# Gọi hàm để thực hiện khử tiếng ồn cho tất cả các tệp trong thư mục và lưu kết quả vào thư mục khác
reduce_noise_in_folder(input_noise_folder, output_remove_noise_folder)

# rate, data = wavfile.read("wav_down/1.wav")
# # perform noise reduction
# reduced_noise = nr.reduce_noise(y=data, sr=rate)
# wavfile.write("renoise_wavs/1.wav", rate, reduced_noise)