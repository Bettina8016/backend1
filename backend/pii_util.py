from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern, RecognizerResult
from presidio_anonymizer import AnonymizerEngine

# Initialize the analyzer and anonymizer engines
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# Define custom recognizer for credit card detection with BIN information
class CreditCardRecognizer(PatternRecognizer):
    def __init__(self):
        patterns = [
            Pattern("Credit card number (weak)", r"\b\d{13,19}\b", 0.5)
        ]
        super().__init__(supported_entity="CREDIT_CARD", patterns=patterns)

    def analyze(self, text, entities, nlp_artifacts=None):
        results = super().analyze(text, entities, nlp_artifacts)
        for result in results:
            if result.entity_type == "CREDIT_CARD":
                result.entity_type = self.get_card_type(text[result.start:result.end])
        return results

    def get_card_type(self, card_number):
        bin_number = card_number[:6]  # BIN is usually the first 6 digits
        if bin_number.startswith('4'):
            return "VISA"
        elif bin_number[:2] in ['51', '52', '53', '54', '55']:
            return "MASTERCARD"
        elif bin_number[:4] == '6011' or bin_number[:3] in ['644', '645', '646', '647', '648', '649'] or bin_number[:2] == '65':
            return "DISCOVER"
        elif bin_number[:2] == '34' or bin_number[:2] == '37':
            return "AMEX"
        else:
            return "UNKNOWN"

# Add custom recognizer to the analyzer
credit_card_recognizer = CreditCardRecognizer()
analyzer.registry.add_recognizer(credit_card_recognizer)

def analyze_pii(text):
    # Analyze the text to detect sensitive information
    results = analyzer.analyze(text=text, entities=[], language='en')
    return results

def anonymize_text(text, analyzer_results):
    # Anonymize identified entities
    anonymized_result = anonymizer.anonymize(text=text, analyzer_results=analyzer_results)
    return anonymized_result