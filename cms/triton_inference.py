import os

import tritonclient.http as httpclient
import numpy as np
import youtokentome as yttm
import cv2


class TritonClient:

    mean = [0.48145466, 0.4578275, 0.40821073]
    std = [0.26862954, 0.26130258, 0.27577711]
    eos_id = 3
    bos_id = 2
    unk_id = 1
    pad_id = 0

    def __init__(self, url, tokenizer_path, dim=(224, 224), text_seq_length=77):
        self.client = httpclient.InferenceServerClient(url=url)
        
        self.dim = dim
        self.text_seq_length = text_seq_length
        self.tokenizer = yttm.BPE(tokenizer_path)

    def vect_l2_norm(self, vector):
        norm=np.linalg.norm(vector)
        if norm==0:
            norm=np.finfo(vector.dtype).eps
        return vector/norm
    
    def _prepocess_img(self, img_path):
        img  = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_preprocessed = cv2.resize(img, self.dim, interpolation=cv2.INTER_LINEAR)
        img_preprocessed = (img_preprocessed.astype("float32")-self.mean) / self.std
        img_preprocessed = img_preprocessed.astype("float32").transpose(2, 0, 1)
        img_preprocessed = np.expand_dims(img_preprocessed, axis=0)
        return img_preprocessed

    def _prepocess_text(self, text):
        text = text.lower()
        tokens = self.tokenizer.encode([text], output_type=yttm.OutputType.ID, dropout_prob=0.0)[0]
        tokens = tokens[:self.text_seq_length-2]
        tokens = [self.bos_id] + tokens + [self.eos_id]
        tokens.extend([self.pad_id for _ in range(self.text_seq_length-len(tokens))])
        token_input = np.array(tokens, dtype=np.int64)
        token_input = np.expand_dims(token_input, axis=0)
        return token_input
    
    def _get_res_text(self, text_input):
        triton_input = httpclient.InferInput(
            "input", text_input.shape, datatype="INT64"
        )
        triton_input.set_data_from_numpy(text_input, binary_data=True)
        outputs = self.client.infer(model_name="clip_textual", inputs=[triton_input])
        out = outputs.as_numpy("output")[0]
        return out

    def _get_res_img(self, img_input):
        triton_input = httpclient.InferInput(
            "input", img_input.shape, datatype="FP32"
        )
        triton_input.set_data_from_numpy(img_input, binary_data=True)
        outputs = self.client.infer(model_name="clip_visual", inputs=[triton_input])
        out = outputs.as_numpy("output")[0]
        return out
    
    def inference_text(self, text: str) -> np.array:
        """Get text embedding"""

        text_preprocessed = self._prepocess_text(text)
        result = self._get_res_text(text_preprocessed)
        result = self.vect_l2_norm(result)
        return result


    def inference_image(self, img_path: str) -> np.array:
        """Get image embedding"""
        if not os.path.exists(img_path):
            raise ValueError('Image file not found')
        img_preprocessed = self._prepocess_img(img_path)
        result = self._get_res_img(img_preprocessed)
        result = self.vect_l2_norm(result)
        return result
    