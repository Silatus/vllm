from vllm import LLM, SamplingParams

model = LLM(
    "nm-testing/zephyr-50sparse-24", 
    sparsity="sparse_w16a16",   # If left off, model will be loaded as dense
    enforce_eager=True,         # Does not work with cudagraphs yet
    dtype="float16",
    tensor_parallel_size=1,
    max_model_len=1024
)

sampling_params = SamplingParams(max_tokens=100, temperature=0)
outputs = model.generate("Hello my name is", sampling_params=sampling_params)
outputs[0].outputs[0].text