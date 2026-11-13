"""Create the fixed pre-retrieval benchmark; fail if any evidence is absent."""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'huggingface_transformers_nlp'

# id, split, source unit, question, answer, exact evidence, type, filter
ROWS = [
('Q01','dev','chapter1/3','Why is the zero-shot classification pipeline described as zero-shot?','It can classify using supplied labels without fine-tuning on the user’s data.',"This pipeline is called _zero-shot_ because you don't need to fine-tune the model on your data to use it. It can directly return probability scores for any list of labels you want!",'direct',None),
('Q02','dev','chapter1/3','What happens when the same default sentiment analysis model is used again after its first download?','The cached model is reused, so it need not be downloaded again.','The model is downloaded and cached when you create the `classifier` object. If you rerun the command, the cached model will be used instead and there is no need to download the model again.','conditional',None),
('Q03','dev','chapter1/4','In chapter 1, how is the general pretrained language model adapted to a specific task?','Through transfer learning or fine-tuning using human-annotated labels for the task.','Because of this, the general pretrained model then goes through a process called *transfer learning* or *fine-tuning*. During this process, the model is fine-tuned in a supervised way -- that is, using human-annotated labels -- on a given task.','filter',{'chapter':'chapter1'}),
('Q04','dev','chapter1/5','In masked language modeling, how does an encoder learn from a sentence?','It predicts original masked tokens using surrounding context.','**Masked language modeling (MLM)**: Used by encoder models like BERT, this approach randomly masks some tokens in the input and trains the model to predict the original tokens based on the surrounding context.','paraphrase',None),
('Q05','dev','chapter1/6','What prediction objective is usually used when pretraining decoder models?','Predicting the next word in the sentence.','The pretraining of decoder models usually revolves around predicting the next word in the sentence.','direct',None),
('Q06','dev','chapter2/2','How should preprocessing compare with the preprocessing used when the model was pretrained?','It must be performed in exactly the same way.','All this preprocessing needs to be done in exactly the same way as when the model was pretrained,','direct',None),
('Q07','dev','chapter2/3','What does AutoModel do when given a checkpoint?','It fetches the appropriate architecture and instantiates the correct model class.',"The `AutoModel` class and its associates are actually simple wrappers designed to fetch the appropriate model architecture for a given checkpoint. It's an \"auto\" class meaning it will guess the appropriate model architecture for you and instantiate the correct model class.",'paraphrase',None),
('Q08','dev','chapter2/4','In chapter 2, what token is used to represent words absent from the vocabulary?','An unknown token, often represented as [UNK] or &lt;unk&gt;.','Finally, we need a custom token to represent words that are not in our vocabulary. This is known as the "unknown" token, often represented as "[UNK]" or "&lt;unk&gt;".','filter',{'chapter':'chapter2'}),
('Q09','dev','chapter2/6','For DistilBERT, what inputs does the tokenizer return as necessary for the model in the example?','Input IDs and the attention mask.','For DistilBERT, that includes the input IDs as well as the attention mask.','direct',None),
('Q10','dev','chapter3/3','What limitation is mentioned for running Trainer.train() without a GPU?','Training runs very slowly on a CPU.',"The hardest part is likely to be preparing the environment to run `Trainer.train()`, as it will run very slowly on a CPU.",'conditional',None),
('Q11','dev','chapter3/5','What might a learning curve that is too erratic or too flat suggest about the learning rate?','Too erratic can indicate a high learning rate; too flat can indicate a low learning rate.','**Learning rate**: Are the curves too erratic (LR too high) or too flat (LR too low)?','conditional',None),
('Q12','dev','chapter4/2','Which checkpoint does the course choose for the French mask-filling example?','camembert-base.','We select the `camembert-base` checkpoint to try it out.','direct',None),
('Q13','dev','chapter4/3','After training finishes, what does trainer.push_to_hub() do in the described workflow?','It uploads the last model version and generates a model card with relevant metadata.','Once your training is finished, you should do a final `trainer.push_to_hub()` to upload the last version of your model. It will also generate a model card with all the relevant metadata, reporting the hyperparameters used and the evaluation results!','conditional',None),
('Q14','dev','chapter4/4','Where is the model card created in the described repository?','In the README.md Markdown file.','Creating the model card is done through the *README.md* file you saw earlier, which is a Markdown file.','direct',None),
('Q15','dev','chapter1/5','Can GPT-2 attend to tokens that occur later in the sequence during masked self-attention?','No; it can attend only to tokens on its left.',"Within each decoder block, GPT-2 uses a *masked self-attention* layer which means GPT-2 can't attend to future tokens. It is only allowed to attend to tokens on the left.",'conditional',None),
('Q16','test','chapter6/4','In chapter 6, which two preprocessing steps occur before the tokenizer splits text into subtokens?','Normalization and pre-tokenization.','Before splitting a text into subtokens (according to its model), the tokenizer performs two steps: _normalization_ and _pre-tokenization_.','filter',{'chapter':'chapter6'}),
('Q17','test','chapter6/5','What happens in the described BPE approach if an input character was absent from the training corpus?','It is converted to the unknown token.','If an example you are tokenizing uses a character that is not in the training corpus, that character will be converted to the unknown token.','conditional',None),
('Q18','test','chapter6/6','How certain is the course’s explanation of the WordPiece training algorithm?','It is a best guess based on published literature and may not be completely accurate.',"Google never open-sourced its implementation of the training algorithm of WordPiece, so what follows is our best guess based on the published literature. It may not be 100% accurate.",'paraphrase',None),
('Q19','test','chapter6/7','How does Unigram change its vocabulary during training compared with BPE and WordPiece?','It starts with a large vocabulary and removes tokens until the desired size is reached.','Compared to BPE and WordPiece, Unigram works in the other direction: it starts from a big vocabulary and removes tokens from it until it reaches the desired vocabulary size.','paraphrase',None),
('Q20','test','chapter7/3','When the pretraining corpus differs little from the fine-tuning corpus, what does the course say about transfer learning?','Transfer learning will usually produce good results.','Provided that the corpus used for pretraining is not too different from the corpus used for fine-tuning, transfer learning will usually produce good results.','conditional',None),
]

def normalize(text):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', text)).strip()

manifest = json.loads((ROOT / 'data/manifest.json').read_text(encoding='utf-8-sig'))
units = {unit['unit_id']: unit for unit in manifest['units']}
questions = []
for qid, split, unit_id, question, answer, evidence, kind, query_filter in ROWS:
    unit = units[unit_id]
    text = (ROOT / unit['path']).read_text(encoding='utf-8')
    if normalize(evidence) not in normalize(text):
        raise ValueError(f'{qid}: evidence absent from {unit_id}')
    if query_filter and query_filter['chapter'] != unit['chapter']:
        raise ValueError(f'{qid}: filter conflicts with source chapter')
    questions.append({'id':qid, 'split':split, 'type':kind, 'question':question,
        'expected_answer':answer, 'gold_source_id':SOURCE, 'gold_page':unit_id,
        'evidence_quote':evidence, 'filter':query_filter})

assert len(questions) == 20 and sum(q['split'] == 'dev' for q in questions) == 15
assert len({q['id'] for q in questions}) == 20
assert sum(q['filter'] is not None for q in questions) >= 3
assert any(q['split'] == 'test' and q['filter'] for q in questions)
(ROOT / 'benchmark/questions.json').write_text(json.dumps(questions, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('Validated 20 evidence passages, 15 dev / 5 test, with 3 metadata filters.')
