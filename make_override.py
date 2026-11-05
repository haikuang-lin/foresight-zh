#!/usr/bin/env python3
"""Writes pipeline_override.pb: the SpeechPipelineOptionsProto the shim substitutes for Foresight's own."""
import sys

def varint(n):
    out = b""
    while True:
        b = n & 0x7F; n >>= 7
        if n: out += bytes([b | 0x80])
        else: return out + bytes([b])

def f_varint(num, v): return varint(num << 3) + varint(v)
def f_bytes(num, b):
    if isinstance(b, str): b = b.encode()
    return varint(num << 3 | 2) + varint(len(b)) + b

INSTRUCTION = ("請逐字轉寫這段語音，保持說話時使用的語言。"
               "中文一律用繁體字（台灣正體）書寫，英文單詞保持英文原樣。只輸出轉寫內容，不要翻譯或解釋。")

prompt = (f_bytes(1, INSTRUCTION) + f_bytes(2, "<|turn>user\n") + f_bytes(3, "<|turn>model\n")
          + f_bytes(4, "<turn|>\n"))
advanced = f_varint(1, int(sys.argv[2]) if len(sys.argv) > 2 else 1600)   # max_spectrogram_columns_per_session
litertlm = (f_varint(1, 48000) + f_varint(2, 1) + f_varint(3, 0) + f_varint(4, 0)
            + f_bytes(5, prompt) + f_bytes(6, advanced))
spo = f_bytes(1000, litertlm)            # SpeechProcessorOptionsProto extension 1000
pipeline = f_bytes(1, spo)               # SpeechPipelineOptionsProto.speech_processor_options
out = sys.argv[1] if len(sys.argv) > 1 else "pipeline_override.pb"
open(out, "wb").write(pipeline)
print(f"wrote {out} ({len(pipeline)} bytes)")
