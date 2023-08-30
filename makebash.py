num_lines = 194

with open("output.txt", "w") as file:
    for i in range(1, num_lines + 1):
        line = f"whisperx renoise_wavs/{i}.wav --compute_type float32 --language vi -o srt\n"
        file.write(line)

print("Tạo tệp thành công: output.txt")