
from typing import *

import func
from geometry import Coord
from tree import UniqueNodeLinks


class LinkedListNode:
    pass


class TextFormat:
    def __init__(self, text: str, width: int):
        self.text = text
        self.width = width

    def next_line_start(self, start_offset: int):
        max_end_offset = end_offset = start_offset + self.width

        if len(self.text) <= max_end_offset:
            end_offset = len(self.text)
        elif self.text[max_end_offset] == ' ':
            # Bump the offset by 1 the next line is "hidden"
            end_offset = max_end_offset + 1
        else:
            for end_offset in range(max_end_offset, start_offset, -1):
                chr_index = self.text[end_offset - 1]
                if chr_index == ' ':
                    break

        return end_offset

    def get_line_offsets(self):
        return func.iterate(
            func=self.next_line_start,
            exit_condition=lambda offset: offset >= len(self.text),
            initial_value=0,
            include_first=True,
            include_last=False
        )

    def get_lines(self) -> List[str]:
        line_offsets = self.get_line_offsets()
        return [
            self.text[begin:end]
            for begin, end
            in zip(line_offsets, line_offsets[1:] + [len(self.text)])
        ]


class Paragraph:

    def __init__(self, text: str):
        self.text = text

    def add_character(self, char, char_offset):
        self.text = self.text[:char_offset] + char + self.text[char_offset:]

    def remove_character(self, char_offset):
        self.text = self.text[:char_offset] + self.text[char_offset + 1:]

    def num_rows(self, row_width):
        return max(1, len(self.text) // row_width)

    def num_chars(self):
        return len(self.text)


class ParagraphId(int):
    @staticmethod
    def invalid() -> 'ParagraphId':
        return ParagraphId(-1)

    def is_valid(self) -> bool:
        return self != ParagraphId.invalid()

    def __bool__(self):
        return self.is_valid()


class ParagraphNodes(Dict[ParagraphId, Paragraph]):
    def __setitem__(self, key, value):
        assert key not in self
        return super().__setitem__(key, value)


class LinkedListParagraphs(UniqueNodeLinks[ParagraphId, None]):

    first: ParagraphId
    last: ParagraphId

    last_unique_id = -1

    @classmethod
    def _get_unique_id(cls) -> ParagraphId:
        cls.last_unique_id += 1
        return ParagraphId(cls.last_unique_id)

    def __init__(self, paragraphs: Iterable[Paragraph]):
        super().__init__()
        self.first = ParagraphId.invalid()
        self.last = ParagraphId.invalid()

        self.paragraph_map = ParagraphNodes()
        for p in paragraphs:
            self.add_paragraph_to_end(p)

    def get_next(self, _id: ParagraphId) -> ParagraphId:
        return super().get_next(_id, None)

    def get_previous(self, _id: ParagraphId) -> ParagraphId:
        if (previous := super().get_previous(_id)) is not None:
            return previous[0]

    def add_paragraph_to_end(self, p: Paragraph) -> ParagraphId:
        new_id = self._get_unique_id()
        self.paragraph_map[new_id] = p
        if not self.first:
            self.first = self.last = new_id
        else:
            self.insert_after(new_id, self.last)
            self.last = new_id

        return new_id

    def insert_after(self, new_id: ParagraphId, previous_id: ParagraphId):
        self.add_link(new_id, previous_id, link_type=None)

    def get_ordered_ids(self) -> List[ParagraphId]:
        return func.iterate(
            self.get_next,
            lambda _id: _id == self.last,
            initial_value=self.first,
            include_first=True,
            include_last=True
        )

    def __iter__(self) -> Iterable[Paragraph]:
        for _id in self.get_ordered_ids():
            yield self[_id]

    def __getitem__(self, item: ParagraphId):
        return self.paragraph_map.get(item)

    def __len__(self):
        return len(self.paragraph_map)


class Cursor:
    p_id: ParagraphId
    offset: int

    def __init__(self, p_id: ParagraphId, offset: int):
        self.p_id = p_id
        self.offset = offset

    def with_offset(self, offset: int) -> 'Cursor':
        return Cursor(
            self.p_id,
            offset
        )

    def with_offset_incr(self, n: int) -> 'Cursor':
        return self.with_offset(self.offset + n)

    def __eq__(self, other: 'Cursor'):
        return self.p_id == other.p_id and self.offset == other.offset


class CalculateCursor:
    text_editor: 'TextEditor'

    def __init__(self, text_editor: 'TextEditor'):
        self.text_editor = text_editor

    @property
    def cursor(self) -> Cursor:
        return self.text_editor.cursor

    @property
    def paragraphs(self) -> LinkedListParagraphs:
        return self.text_editor.paragraphs

    def get_cursor_coord(self, width: int) -> Coord:
        assert len(self.paragraphs) == 1  # This is quick and dirty for the case of 1 paragraph

        lines_offsets = TextFormat(self.paragraph.text, width).get_line_offsets()

        prev_line_offset = 0
        i = 0
        for i, line_offset in enumerate(lines_offsets):
            if line_offset > self.cursor.offset:
                y = i - 1
                break
            prev_line_offset = line_offset
        else:
            y = i

        x = self.cursor.offset - prev_line_offset

        # The offset can be a bit wider than the width in a couple cases.
        # (1) There is a space at the beginning of the next row, which is "hidden" by absorbing it into the previous row
        # (2) If the cursor is at the end of the paragraph then it is one beyond the length of the actual text. If the
        #     last row is full, then the cursos will be off the end by one.
        if x >= width:
            x = 0
            y += 1

        return Coord(x=x, y=y)

    def get_offset_from_coord(self, width: int, coord: Coord) -> int:
        line_offsets = TextFormat(self.paragraph.text, width).get_line_offsets()
        assert coord.y < len(line_offsets)
        new_offset = line_offsets[coord.y] + coord.x
        return new_offset

    @property
    def paragraph(self) -> Paragraph:
        return self.paragraphs[self.cursor.p_id]

    # @property
    # def offset(self) -> int:
    #     return self.cursor.offset

    def get_paragraph_origin(self, _id: ParagraphId):
        if (p := self.paragraphs[_id]) is not None:
            return Cursor(
                _id,
                0
            )

    def get_paragraph_end(self, _id: ParagraphId):
        if (p := self.paragraphs[_id]) is not None:
            return Cursor(
                _id,
                p.num_chars()
            )

    def is_origin(self):
        return self.cursor.offset == 0

    def is_end(self):
        return self.cursor.offset == self.paragraph.num_chars()

    def get_incr_cursor(self) -> Cursor:
        if not self.is_end():
            return self.cursor.with_offset(self.cursor.offset + 1)
        elif next_paragraph_id := self.paragraphs.get_next(self.cursor.p_id):
            return self.get_paragraph_origin(next_paragraph_id)
        else:
            return self.cursor

    def get_decr_cursor(self) -> Cursor:
        if not self.is_origin():
            return self.cursor.with_offset(self.cursor.offset - 1)
        elif prev_p_id := self.paragraphs.get_previous(self.cursor.p_id):
            return self.get_paragraph_end(prev_p_id)
        else:
            return self.cursor

    def __get_corrected_cursor_for_coord(self, width: int, coord: Coord) -> Cursor:
        lines = TextFormat(self.paragraph.text, width).get_lines()

        if coord.y < 0:
            return self.cursor.with_offset(0)
        elif coord.y >= len(lines):
            return self.get_paragraph_end(self.cursor.p_id)

        new_y = coord.y
        new_x = min(coord.x, len(lines[new_y]))
        new_offset = self.get_offset_from_coord(width, Coord(x=new_x, y=new_y))
        return self.cursor.with_offset(new_offset)

    def get_cursor_for_incr_row(self, width) -> Cursor:
        coord_uncorrected = self.get_cursor_coord(width)
        coord_uncorrected.y += 1
        return self.__get_corrected_cursor_for_coord(width, coord_uncorrected)

    def get_cursor_for_decr_row(self, width) -> Cursor:
        coord_uncorrected = self.get_cursor_coord(width)
        coord_uncorrected.y -= 1
        return self.__get_corrected_cursor_for_coord(width, coord_uncorrected)


class TextEditor:

    paragraphs: LinkedListParagraphs
    cursor: Cursor
    calculate_cursor: CalculateCursor

    def __init__(self, text: str):
        self.paragraphs = LinkedListParagraphs(Paragraph(p) for p in text.split('\n'))
        self.cursor = Cursor(self.paragraphs.first, 0)
        self.calculate_cursor = CalculateCursor(self)

    @property
    def active_paragraph(self) -> Paragraph:
        return self.paragraphs[self.cursor.p_id]

    def add_character(self, c: str, cursor: Cursor):
        self.paragraphs[cursor.p_id].add_character(c, cursor.offset)

    def remove_character(self, cursor: Cursor):
        paragraph = self.paragraphs[cursor.p_id]
        if cursor.offset < paragraph.num_chars():
            paragraph.remove_character(cursor.offset)

        # if self.cursor.is_origin() and self.cursor.paragraph_index == 0:
        #     return
        # elif self.cursor.is_origin():
        #     new_cursor = self.get_previous_paragraph(self.cursor.paragraph).end()
        #     self.merge_paragraphs_at_cursor()
        #     self.cursor = new_cursor
        # else:
        #     self.cursor.paragraph.remove_character(self.cursor.paragraph_row, self.cursor.column)

    # def split_paragraph_at_cursor(self):
    #     this_paragraph = self.cursor.paragraph
    #     char_offset = this_paragraph.get_char_offset(self.cursor.paragraph_row, self.cursor.column)
    #     text1, text2 = this_paragraph.text[:char_offset], this_paragraph.text[char_offset:]
    #     this_paragraph.text = text1
    #     new_paragraph = Paragraph(text2, self.width)
    #     self.add_paragraph_after(new_paragraph, this_paragraph)
    #
    # def merge_paragraphs_at_cursor(self):
    #     this_paragraph = self.cursor.paragraph
    #     previous_paragraph = self.get_previous_paragraph(this_paragraph)
    #     if not previous_paragraph:
    #         return
    #
    #     new_text = previous_paragraph.text + this_paragraph.text
    #     previous_paragraph.text = new_text
    #     self.remove_paragraph(this_paragraph)

    def get_data(self):
        return '\n'.join(p.text for p in self.paragraphs)
