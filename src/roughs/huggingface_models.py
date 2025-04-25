from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "Qwen/Qwen2.5-Coder-14B-Instruct"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

prompt = """
    (type cutting)
    (object (an object
    (type tomato)
    (name "tomato")
    (properties (size "medium")
    (texture "smooth")
    (color "red"))))
    (location (an location
    (type table)
    (name "table)
    (properties (material "wood")
    (height 0.75)
    (accessibility "high")
    (surface-type "stable"))))
    
    assume this as CRAM action designator for task instruction like cut the tomato on the table.
    generate action designator for the task instruction like cut the eggplant using the small black knife
    """
messages = [
    {"role": "system", "content": "You are smart agent able to generate CRAM action designator for task instruction."},
    {"role": "user", "content": prompt}
]
text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)
model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=512
)
generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
]

response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

print(response)
