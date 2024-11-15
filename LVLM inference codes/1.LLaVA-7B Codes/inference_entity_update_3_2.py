from vis_corrector_recap import Corrector
from types import SimpleNamespace
import argparse
import json
import gc
import transformers, torch, spacy, os
from tqdm import tqdm
from typing import Dict, List
from transformers import pipeline, Blip2Processor, Blip2ForConditionalGeneration, InstructBlipProcessor, InstructBlipForConditionalGeneration


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Code for 'ReCaption'.")
    parser.add_argument('--stage-1', default='./Each_stage_texts/Ours_llava_7b_entity_instructblip_3_2.json')
    parser.add_argument('--query', default='Describe this image.', type=str, help="text query for MLLM")
    parser.add_argument('--cache-dir', type=str, default='./cache_dir')
    parser.add_argument('--detector-config',
                        default='/home/fjq/MLLMs/Woodpecker/groundingdino/config/GroundingDINO_SwinT_OGC.py', type=str,
                        help="Path to the detector config, \
                                in the form of 'path/to/GroundingDINO_SwinT_OGC.py' ")
    parser.add_argument('--detector-model', default='/data/fjq/3.VLMS/Woodpecker/groundingdino_swint_ogc.pth', type=str,
                        help="Path to the detector checkpoint, \
                                in the form of 'path/to/groundingdino_swint_ogc.pth' ")


    args = parser.parse_args()
    
    args_dict = {
        'cache_dir': args.cache_dir,
        'detector_config': args.detector_config,
        'detector_model_path': args.detector_model,
}

    model_args = SimpleNamespace(**args_dict)
    # pipeline = transformers.pipeline(
    #         "text-generation", model='/data/lqf_llama/Meta-Llama-3-8B-Instruct',
    #         model_kwargs={"torch_dtype": torch.float32},
    #         device_map={"": 0}
    #     )
    pipeline = 1

    ########
    # model_blip = Blip2ForConditionalGeneration.from_pretrained('/data/fjq/blip-2/blip2-flan-t5-xxl',
    #                                                            torch_dtype=torch.float32)  # , load_in_8bit=True)
    # model_blip.to("cuda:0")
    # processor_blip = Blip2Processor.from_pretrained('/data/fjq/blip-2/blip2-flan-t5-xxl')
    ########
    # model_instructblip = InstructBlipForConditionalGeneration.from_pretrained('/data/fjq/blip-2/Instructblip-flan-t5-xxl',
    #                                                            torch_dtype=torch.float32)  # , load_in_8bit=True)
    # model_instructblip.to("cuda:0")
    # processor_instructblip = InstructBlipProcessor.from_pretrained('/data/fjq/blip-2/Instructblip-flan-t5-xxl')
    ########


    ###################################################################################################### Instructblip-vicuna-13b
    model_instructblip_vicuna = InstructBlipForConditionalGeneration.from_pretrained('/data/fjq/blip-2/Instructblip-vicuna-13b',
                                                                   torch_dtype=torch.float32)  # , load_in_8bit=True)
    model_instructblip_vicuna.to("cuda:0")
    processor_instructblip_vicuna = InstructBlipProcessor.from_pretrained('/data/fjq/blip-2/Instructblip-vicuna-13b')
    ################################################################################################################


    corrector = Corrector(model_args)
    final_text = []

    ##所有的coda图片的详细描述，存到列表中
    with open(args.stage_1, 'r', encoding='utf-8') as f:
        coda_detail_captions = json.load(f)

    coda_detail_captions_correct = []
    for sample in coda_detail_captions:
        output = corrector.correct(pipeline, pipeline, pipeline, pipeline, pipeline,
                                   processor_instructblip_vicuna, model_instructblip_vicuna,
                                   sample)
        print(output)
        coda_detail_captions_correct.append(output)
        print(len(coda_detail_captions_correct))


    with open('./Each_stage_texts/Ours_llava_7b_entity_update_3_2.json', 'w', encoding='utf-8') as f:
        json.dump(coda_detail_captions_correct, f, indent=4, ensure_ascii=False)




