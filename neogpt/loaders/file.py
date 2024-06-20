import json

from loaders.base import BaseLoader


class TxtLoader(BaseLoader):
    def load(self):
        with open(self.path) as f:
            return f.read()

    def lazy_load(self):
        with open(self.path) as f:
            yield from f


class JSONLoader(BaseLoader):
    def load(self):
        with open(self.path) as f:
            return json.load(f)

    def lazy_load(self):
        with open(self.path) as f:
            yield from json.load(f)


class PDFLoader(BaseLoader):
    def __init__(self, path: str):
        try:
            from pdfminer.high_level import extract_text
        except ImportError as err:
            raise ImportError("""
                Please install pdfminer.six to use the PDFLoader.
                You can install it using:
                `pip install pdfminer.six`
            """) from err

        super().__init__(path)

    def load(self):
        from pdfminer.high_level import extract_text

        return extract_text(self.path)

    def lazy_load(self):
        from pdfminer.high_level import extract_text

        yield extract_text(self.path)


class CSVLoader(BaseLoader):
    def __init__(self, path: str):
        try:
            import pandas as pd
        except ImportError as err:
            raise ImportError("""
                Please install pandas to use the CSVLoader.
                You can install it using:
                `pip install pandas`
            """) from err

        super().__init__(path)

    def load(self):
        import pandas as pd

        return pd.read_csv(self.path, engine="pyarrow")

    def lazy_load(self):
        import pandas as pd

        yield pd.read_csv(self.path)


class TSVLoader(BaseLoader):
    def __init__(self, path: str):
        try:
            import pandas as pd
        except ImportError as err:
            raise ImportError("""
                Please install pandas to use the TSVLoader.
                You can install it using:
                `pip install pandas`
            """) from err

        super().__init__(path)

    def load(self):
        import pandas as pd

        return pd.read_csv(self.path, sep="\t", engine="pyarrow")

    def lazy_load(self):
        import pandas as pd

        yield pd.read_csv(self.path, sep="\t")


class MarkdownLoader(BaseLoader):
    def __init__(self, path: str):
        try:
            import markdown
        except ImportError as err:
            raise ImportError("""
                Please install markdown to use the MarkdownLoader.
                You can install it using:
                `pip install markdown`
            """) from err

        super().__init__(path)

    def load(self):
        import markdown

        with open(self.path) as f:
            return markdown.markdown(f.read())

    def lazy_load(self):
        import markdown

        with open(self.path) as f:
            yield markdown.markdown(f.read())




class HTMLLoader(BaseLoader):
    def __init__(self, path: str):
        try:
            from bs4 import BeautifulSoup
        except ImportError as err:
            raise ImportError("""
                Please install beautifulsoup4 to use the HTMLLoader.
                You can install it using:
                `pip install beautifulsoup4`
            """) from err

        super().__init__(path)

    def load(self):
        from bs4 import BeautifulSoup
        with open(self.path, encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            # Extract text content excluding HTML tags
            return soup.get_text(separator="\n", strip=True)

    def lazy_load(self):
        from bs4 import BeautifulSoup
        with open(self.path, encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            # Yield clean text content in chunks
            yield soup.get_text(separator="\n", strip=True)


class DocxLoader(BaseLoader):
    def __init__(self, path: str):
        try:
            from docx import Document
        except ImportError as err:
            raise ImportError("""
                Please install python-docx to use the DocxLoader.
                You can install it using:
                `pip install python-docx`
            """) from err

        super().__init__(path)

    def load(self):
        from docx import Document
        doc = Document(self.path)
        return "\n".join([p.text for p in doc.paragraphs])

    def lazy_load(self):
        from docx import Document
        doc = Document(self.path)
        for p in doc.paragraphs:
            yield p.text


class PPTXLoader(BaseLoader):
    def __init__(self, path: str):
        try:
            from pptx import Presentation
        except ImportError as err:
            raise ImportError("""
                Please install python-pptx to use the PPTXLoader.
                You can install it using:
                `pip install python-pptx`
            """) from err

        super().__init__(path)

    def load(self):
        from pptx import Presentation
        prs = Presentation(self.path)
        return "\n".join([slide.text for slide in prs.slides])

    def lazy_load(self):
        from pptx import Presentation
        prs = Presentation(self.path)
        for slide in prs.slides:
            yield slide.text


class XLSXLoader(BaseLoader):
    def __init__(self, path: str):
        try:
            import pandas as pd
        except ImportError as err:
            raise ImportError("""
                Please install pandas to use the XLSXLoader.
                You can install it using:
                `pip install pandas`
            """) from err

        super().__init__(path)

    def load(self):
        import pandas as pd
        return pd.read_excel(self.path)

    def lazy_load(self):
        import pandas as pd
        yield pd.read_excel(self.path)




LOADER_MAP = {
    ".txt": TxtLoader,
    ".json": JSONLoader,
    ".pdf": PDFLoader,
    ".csv": CSVLoader,
    ".tsv": TSVLoader,
    ".md": MarkdownLoader,
    ".html": HTMLLoader,
    ".doc": DocxLoader,
    ".docx": DocxLoader,
    ".pptx": PPTXLoader,
    ".ppt": PPTXLoader,
    ".xlsx": XLSXLoader,
    ".xls": XLSXLoader,
}
