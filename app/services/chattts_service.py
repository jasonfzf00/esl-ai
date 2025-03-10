import ChatTTS
import os
import torch
import torchaudio
import soundfile
import numpy as np
import time
import random
from huggingface_hub import snapshot_download

module_name = "chattts_service"

# Model path for ChatTTS (text to speech model)
MODELPATH = "./chattts/ChatTTS/asset"
VOICE_MODEL_PATH = "./chattts/voice-presets"
 
class ChatttsService:
    def __init__(self,
                 modelPath=MODELPATH,
                 saveFilePath="output/",
                 gender="male",
                 fixSpkStyle=True):
        
        # Download the model from Huggingface if not exists
        if not os.path.exists(modelPath):
            repo_id = "2Noise/ChatTTS"
            destination_path = "./chattts/ChatTTS"  
            snapshot_download(repo_id=repo_id, local_dir=destination_path)
            print(f"Repository cloned to: {destination_path}")
            
        self.modelPath = modelPath
        self.wavfilePath = saveFilePath
        self.fixSpkStyle = fixSpkStyle
        
        # Initialize ChatTTS
        print("Initializing ChatTTS...")
        self.chat = ChatTTS.Chat()
        try:
            self.chat.load(custom_path=modelPath)
            print("ChatTTS initialized successfully")
        except Exception as e:
            print(f"Error initializing ChatTTS: {str(e)}")
            raise
        
        # Set up text refinement parameters
        self.params_refine_text = ChatTTS.Chat.RefineTextParams(
            prompt='[oral_0][laugh_0][break_0]',
            top_P=0.7,
            top_K=20
        )
        
        try:
            # Load voice model based on gender
            if gender == "male":
                spk_path = f"{VOICE_MODEL_PATH}/seed_1345_male.pt"
            else:
                spk_path = f"{VOICE_MODEL_PATH}/seed_742_female.pt"
                
            print(f"Loading voice model from: {spk_path}")
            spk = torch.load(spk_path, map_location=torch.device('cpu'))
            
            # Set up inference parameters
            self.params_infer_code = ChatTTS.Chat.InferCodeParams(
                spk_emb=spk,
                temperature=0.3,
                prompt="[speed_5]"
            )
            print("Voice model loaded successfully")
            
        except Exception as e:
            print(f"Error loading voice model: {str(e)}")
            raise

    def setRefineTextConf(self, oralConf="[oral_0]", laughConf="[laugh_0]", breakConf="[break_0]"):
        self.params_refine_text = ChatTTS.Chat.RefineTextParams(
            prompt=f"{oralConf}{laughConf}{breakConf}",
            top_P=0.7,
            top_K=20
        )

    # Optional: Config the speech style with random generation
    def setInferCode(self, temperature=0.3, top_P=0.7, top_K=20, speed="[speed_5]"):
        self.params_infer_code = ChatTTS.Chat.InferCodeParams(
            spk_emb=self.params_infer_code.spk_emb,
            temperature=temperature,
            prompt=speed
        )

    def generateSound(self, texts, savePath="output/", filePrefix="output"):
        """
        Generate audio files from text.
        
        Args:
            texts: List of text strings to convert to audio
            savePath: Directory to save the audio files
            filePrefix: Prefix for the audio file names
            
        Returns:
            List of paths to the generated audio files
        """
        # Ensure the save directory exists
        os.makedirs(savePath, exist_ok=True)
        
        # Validate input
        if not texts or not isinstance(texts, list):
            print(f"Warning: Invalid texts input: {texts}")
            return []
            
        # Print debug information
        print(f"Generating audio for texts: {texts}")
        print(f"Save path: {savePath}")
        print(f"File prefix: {filePrefix}")
        
        try:
            # Generate audio using ChatTTS
            wavs = self.chat.infer(
                text=texts,
                stream=False,
                use_decoder=True,
                params_refine_text=self.params_refine_text,
                params_infer_code=self.params_infer_code
            )
            
            # Print debug information about the generated wavs
            print(f"Generated {len(wavs)} audio segments")
            
            # Save each audio file and collect paths
            wavFilePath = []
            for (index, wave) in enumerate(wavs):
                try:
                    # Debug the wave structure
                    print(f"Wave {index} type: {type(wave)}")
                    
                    # Handle different possible wave structures
                    if isinstance(wave, np.ndarray):
                        # If it's a NumPy array, use it directly
                        audio_data = wave
                        print(f"NumPy array shape: {wave.shape}")
                    elif isinstance(wave, (list, tuple)) and len(wave) > 0:
                        # If it's a list or tuple, use the first element
                        audio_data = wave[0]
                        print(f"Using first element of sequence, type: {type(audio_data)}")
                    else:
                        # Fallback
                        audio_data = wave
                        print(f"Using wave directly, type: {type(audio_data)}")
                    
                    # Create the full file path
                    file_path = os.path.join(savePath, f"{filePrefix}{index}.wav")
                    
                    # Save the audio file
                    print(f"Saving audio to: {file_path}")
                    soundfile.write(file_path, audio_data, 24000)
                    
                    # Add the file path to the list
                    wavFilePath.append(file_path)
                    
                except Exception as e:
                    print(f"Error processing wave {index}: {str(e)}")
                    print(f"Wave data type: {type(wave)}")
                    if isinstance(wave, np.ndarray):
                        print(f"Wave shape: {wave.shape}, dtype: {wave.dtype}")
                    continue
                
            return wavFilePath
            
        except Exception as e:
            print(f"Error in generateSound: {str(e)}")
            print(f"Texts: {texts}")
            return []

# if __name__ == "__main__":
#     chUtil = ChatttsService()
#     texts = [
#         "Hi, I'm Jason. Thank you for reaching out!",
#     ]
#     # chUtil.setInferCode(0.8, 0.7, 20, speed="[speed_3]")
#     chUtil.generateSound(texts)