class NormalizationUtils:
    @staticmethod
    def normalize_values(values: list[str]) -> list[str]:
        return [value.lower() for value in values]