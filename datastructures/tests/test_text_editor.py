
from datastructures import text_editor as te


text_1 = (
    "\n"
    "the first line was blank\n"
    " this one has a space at the beginning\n"
    "this one has a space at the end \n"
    "\n"
    "\n"
    "above there are two blank lines, and we'll end with another blank line\n"
    "\n"
)

text_2 = (
    "\n"
    "A\n"
    "\n"
    "B\n"
    "\n"
)


def _build_paragraphs(text: str):
    paragraph_parts = [
        te.Paragraph(part)
        for part in text.split('\n')
    ]
    return te.ParagraphsList(paragraph_parts)


def test_make_paragraphs():
    paragraphs = _build_paragraphs(text_1)
    paragraphs_list = list(paragraphs.iter_values())

    assert paragraphs_list[0].text == ''
    assert paragraphs_list[1].text == 'the first line was blank'
    assert paragraphs_list[2].text == ' this one has a space at the beginning'
    assert paragraphs_list[3].text == 'this one has a space at the end '
    assert paragraphs_list[4].text == ''
    assert paragraphs_list[5].text == ''
    assert paragraphs_list[6].text == 'above there are two blank lines, and we\'ll end with another blank line'
    assert paragraphs_list[7].text == ''


def test_insert_paragraphs():
    paragraphs = _build_paragraphs(text_1)
    paragraphs.insert_item_after(paragraphs.first, te.Paragraph('A'))
    paragraphs.insert_item_after(paragraphs.last, te.Paragraph('B'))

    paragraphs_list = list(paragraphs.iter_values())

    assert paragraphs_list[1].text == 'A'
    assert paragraphs_list[-1].text == 'B'



def _find_paragraph(text_editor: te.TextEditor, paragraph_text: str) -> te.ParagraphId:
    return next(_id for _id, p in text_editor.paragraphs.iter_items() if paragraph_text in p.text)



def test_create_paragraph_at_cursor():
    text_editor = te.TextEditor(text_1)
    paragraph_to_edit = 'this one has a space at the end'
    p_id_to_edit = _find_paragraph(text_editor, paragraph_to_edit)
    cursor = te.Cursor(p_id_to_edit, 6)

    text_editor.split_paragraph(cursor)

    previous_id = text_editor.paragraphs.get_previous(p_id_to_edit)
    new_id = text_editor.paragraphs.get_next(p_id_to_edit)

    assert text_editor.paragraphs[previous_id].text == ' this one has a space at the beginning'
    assert text_editor.paragraphs[p_id_to_edit].text == 'this o'
    assert text_editor.paragraphs[new_id].text == 'ne has a space at the end '


def test_create_paragraph_at_cursor_starting_at_empty_paragraph():
    text_editor = te.TextEditor(text_2)
    paragraphs = text_editor.paragraphs
    first_blank_id = text_editor.paragraphs.first
    second_blank_id = paragraphs.get_next(paragraphs.get_next(first_blank_id))
    third_blank_id = paragraphs.get_next(paragraphs.get_next(second_blank_id))

    text_editor.split_paragraph(te.Cursor(first_blank_id, 0))
    text_editor.split_paragraph(te.Cursor(second_blank_id, 0))
    text_editor.split_paragraph(te.Cursor(third_blank_id, 0))

    paragraphs_list = list(paragraphs.iter_values())
    assert paragraphs_list[0].text == ''
    assert paragraphs_list[1].text == ''
    assert paragraphs_list[2].text == 'A'
    assert paragraphs_list[3].text == ''
    assert paragraphs_list[4].text == ''
    assert paragraphs_list[5].text == 'B'
    assert paragraphs_list[6].text == ''
    assert paragraphs_list[7].text == ''


def test_paragraph_offsets():



    paragraphs = _build_paragraphs(text_1)


    first_p, second_p = paragraphs.iter_values()[:2]

    "the first line was blank\n"


    assert first_p.lines_start_end(width=9) == [
        (0, 0),  # blank line
    ]

    assert second_p.lines_start_end(width=9) == [
        (0, 10),
        (10, 19),  # The first line expanded to "hide" the space character
        (19, 24),
    ]

    all_offsets = list(paragraphs.lines(width=9))
    assert all_offsets[:9] == [
        te.Line(start=0, end=0, row=0, p_id=te.ParagraphId(0)),
        te.Line(start=0, end=10, row=0, p_id=te.ParagraphId(1)),
        te.Line(start=10, end=19, row=1, p_id=te.ParagraphId(1)),
        te.Line(start=19, end=24, row=2, p_id=te.ParagraphId(1)),
        te.Line(start=0, end=10, row=0, p_id=te.ParagraphId(2)),
        te.Line(start=10, end=16, row=1, p_id=te.ParagraphId(2)),
        te.Line(start=16, end=25, row=2, p_id=te.ParagraphId(2)),
        te.Line(start=25, end=29, row=3, p_id=te.ParagraphId(2)),
        te.Line(start=29, end=38, row=4, p_id=te.ParagraphId(2)),
    ]
