import re
from factiva.models import Articles, Transcript

class DbTranscript:
    
    re_pattern = '[A-Z ,-.&]+:'

    def __init__(self, article_text):
        self.article_text = article_text

    def match_split(self):
        speakers = re.findall(self.re_pattern, self.article_text)
        statements = re.split(self.re_pattern, self.article_text)
        statements.pop(0)
        if len(speakers) != len(statements):
            print("Length of strings don't match")
        sequences = []
        for i, speaker in enumerate(speakers):
            seq = {
                'sequence': i,
                'statement': [speaker.rstrip(':'), statements[i]]
            }
            sequences.append(seq)
        
        return sequences
