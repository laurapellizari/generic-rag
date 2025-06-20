from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import ImageRefMode, PictureItem, TableItem
from pathlib import Path
import tempfile

IMAGE_RESOLUTION_SCALE = 2.0

def extract_text_from_pdf(pdf_path: Path, output_dir: Path) -> str:
    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True

    doc_converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    )

    conv_res = doc_converter.convert(pdf_path)
    doc_filename = conv_res.input.file.stem

    output_dir.mkdir(parents=True, exist_ok=True)

    # Salvar imagens de páginas
    for page_no, page in conv_res.document.pages.items():
        img_path = output_dir / f"{doc_filename}-page-{page_no}.png"
        with img_path.open("wb") as fp:
            page.image.pil_image.save(fp, format="PNG")

    # Salvar imagens de tabelas e figuras
    table_counter = 0
    picture_counter = 0
    for element, _ in conv_res.document.iterate_items():
        if isinstance(element, TableItem):
            table_counter += 1
            img_path = output_dir / f"{doc_filename}-table-{table_counter}.png"
            with img_path.open("wb") as fp:
                element.get_image(conv_res.document).save(fp, "PNG")
        elif isinstance(element, PictureItem):
            picture_counter += 1
            img_path = output_dir / f"{doc_filename}-picture-{picture_counter}.png"
            with img_path.open("wb") as fp:
                element.get_image(conv_res.document).save(fp, "PNG")

    # Criar arquivo temporário para o markdown
    with tempfile.NamedTemporaryFile(mode="r+", suffix=".md", delete=False) as tmp_md:
        conv_res.document.save_as_markdown(tmp_md.name, image_mode=ImageRefMode.EMBEDDED)
        tmp_md.seek(0)
        markdown_text = tmp_md.read()

    return markdown_text
