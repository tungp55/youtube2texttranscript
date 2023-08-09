
import whisperx
import glob 
import os
import torch 
from transformers import pipeline





vad_filter = True #@param {type:"boolean"}
hf_token = 'hf_' #@param {type:"string"}
parallel_bs = 4 #@param {type:"integer"}
temperature = 0 #@param {type:"integer"}
temperature_increment_on_fallback = 0.2 #@param {type:"number"}
interpolate_method = 'nearest' #@param {choices:["nearest", "linear", "ignore"]}

align_extend = 2 #@param {type:"integer"}
align_from_prev = True #@param {type:"boolean"}


transcription_cutoff_char = 120 #@param {type:"integer"}
transcription_sentence_interval = 1.5 #@param {type:"number"}

translation_thread = 20 #@param {type:"integer"}
translation_lines_per_request = 10 #@param {type:"integer"}
# device = "cuda"
device = "cuda" if torch.cuda.is_available() else "cpu"

vad_model = 'silero' #@param {choices:["silero", "pya"]}


# if vad_filter:
#     from whisperx.vad import VADSegmentPipeline
#     vad_pipeline = VADSegmentPipeline(model_name = vad_model,
#                                           device = device,
#                                           hf_token = hf_token,
#                                           chunk_length = 30)

# Whisper is on large-v2 by default
model_name = 'large-v2' #@param ["tiny", "small", "medium", "large-v2", "tiny.en", "small.en", "medium.en"]

model = whisperx.load_model(model_name)
audio_file_language = 'vietnamese'



files = [
    # "data/thanhnguyen/inputs/1.wav",
    "mywav_reduced_noise.wav",
    # "data/thanhnguyen/inputs/3.wav",
    # "data/thanhnguyen/inputs/4.wav",
    # "data/thanhnguyen/inputs/5.wav"
]


for file in files:
    audio_path = file
    base_name = os.path.basename(file).split(".")[0]

    

    print("Performing transcription...")
    result = whisperx.transcribe(model, audio_path, temperature=temperature, verbose=True, language=audio_file_language)


    language_code = whisperx.tokenizer.TO_LANGUAGE_CODE.get(result["language"], 'en')



    model_alignment, metadata_alignment = whisperx.alignment.load_align_model(language_code=language_code, device=device)


    result_aligned = whisperx.alignment.align(result["segments"], model_alignment, metadata_alignment, audio_path, device,
                            extend_duration=align_extend, start_from_previous=align_from_prev, interpolate_method=interpolate_method)


    result_merged = result_aligned["segments"]

    import copy

    def word_segment_to_sentence(segments, max_text_len=80):
        """
        Convert word segments to sentences.
        :param segments: [{"text": "Hello,", "start": 1.1, "end": 2.2}, {"text": "World!", "start": 3.3, "end": 4.4}]
        :type segments: list of dicts
        :return: Segments, but with sentences instead of words.
        :rtype: list of dicts  [{"text": "Hello, World!", "start": 1.1, "end": 4.4}]
        """
        end_of_sentence_symbols = tuple(['.', '!', '?', ',', ';', ':'])
        sentence_results = []
        
        current_sentence = {"text": "", "start": 0, "end": 0}
        current_sentence_template = {"text": "", "start": 0, "end": 0}
        
        for segment in segments:
            if current_sentence["text"] == "":
                current_sentence["start"] = segment["start"]
            current_sentence["text"] += ' ' + segment["text"] + ' '
            current_sentence["end"] = segment["end"]
            if segment["text"][-1] in end_of_sentence_symbols:
                current_sentence["text"] = current_sentence["text"].strip()
                sentence_results.append(copy.deepcopy(current_sentence))
                current_sentence = copy.deepcopy(current_sentence_template)
        return sentence_results


    def sentence_segments_merger(segments, max_text_len=80, max_segment_interval=2):
        """
        Merge sentence segments to one segment, if the length of the text is less than max_text_len.
        :param segments: [{"text": "Hello, World!", "start": 1.1, "end": 4.4}, {"text": "Hello, World!", "start": 1.1, "end": 4.4}]
        :type segments: list of dicts
        :param max_text_len: Max length of the text
        :type max_text_len: int
        :return: Segments, but with merged sentences.
        :rtype: list of dicts  [{"text": "Hello, World! Hello, World!", "start": 1.1, "end": 4.4}]
        """
        
        merged_segments = []
        current_segment = {"text": "", "start": 0, "end": 0}
        current_segment_template = {"text": "", "start": 0, "end": 0}
        
        for segment in segments:
            if current_segment["text"] == "":
                current_segment["start"] = segment["start"]


            if segment["start"] - current_segment["end"] < max_segment_interval and \
                    len(current_segment["text"] + " " + segment['text']) < max_text_len:
                print('merge')
                current_segment["text"] += ' ' + segment["text"]
                current_segment["end"] = segment["end"]
            else:
                current_segment["text"] = current_segment["text"].strip()
                merged_segments.append(copy.deepcopy(current_segment))
                current_segment = copy.deepcopy(segment)
        
        return merged_segments


    import srt
    from datetime import timedelta


    result_srt_list = []
    for i, v in enumerate(result_merged):
        result_srt_list.append(srt.Subtitle(index=i, start=timedelta(seconds=v['start']), end=timedelta(seconds=v['end']), content=v['text'].strip()))

    composed_transcription = srt.compose(result_srt_list)

    save_file = f"{base_name}.srt"
    with open(save_file, 'w') as f:
        f.write(composed_transcription)