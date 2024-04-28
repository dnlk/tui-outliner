import operator
from dataclasses import dataclass

from common_imports import *
from datastructures import linked_list

from ext import func
from ext.geometry import Coord
from datastructures.tree import UniqueNodeLinks


class LinkedListNode:
    pass


class TextFormat:
    def __init__(self, text: str, width: int):
        # Newline characters at the end of a paragraph are "hidden". A consequence of the processing is that a newline
        # at the very end of the block will get hidden with the preceeding text, and not display as a new blank line.
        # To fix this, a trailing newline gets padded with a space.
        # Probably, the text protocol should change so that each paragraph always ends with a newline character, even
        # if it is the last paragraph.
        self.text = text + ' ' if text.endswith('\n') else text
        self.width = width

    def next_line_start(self, start_offset: int):
        max_end_offset = end_offset = start_offset + self.width

        this_text = self.text[start_offset:max_end_offset]
        before_newline, *_ = this_text.split('\n', 1)

        if len(before_newline) < len(this_text):
            # There was a newline in this bit of text, so generate a new line
            new_max_end_offset = start_offset + len(before_newline) + 1  # The \n was stripped by `str.split()`
            assert new_max_end_offset <= max_end_offset
            end_offset = new_max_end_offset
        elif len(self.text) <= max_end_offset:
            end_offset = len(self.text)
        elif self.text[max_end_offset] == ' ':
            # Bump the offset by 1, so the space is "hidden"
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
            self.text[begin:end].rstrip('\n')
            for begin, end
            in zip(line_offsets, line_offsets[1:] + [len(self.text)])
        ]


class Paragraph:

    def __init__(self, text: str):
        self.text = text

    def lines_start_end(self, width: int) -> List[Tuple[int, int]]:
        line_starts = TextFormat(self.text, width).get_line_offsets()
        return list(zip(line_starts, line_starts[1:] + [len(self.text)]))

    def add_character(self, char, char_offset):
        self.text = self.text[:char_offset] + char + self.text[char_offset:]

    def remove_character(self, char_offset):
        self.text = self.text[:char_offset] + self.text[char_offset + 1:]

    def num_rows(self, row_width) -> int:
        return max(1, len(self.text) // row_width)

    def num_chars(self) -> int:
        return len(self.text)

    def get_char(self, pos: int) -> str | None:
        if pos < len(self.text):
            return self.text[pos]

    def __repr__(self):
        return self.text


class ParagraphId(int):
    @staticmethod
    def invalid() -> 'ParagraphId':
        return ParagraphId(-1)

    def is_valid(self) -> bool:
        return self != ParagraphId.invalid()

    def __bool__(self):
        return self.is_valid()


class PIDFactory:
    last_unique_id = -1

    def make_unique_id(self) -> ParagraphId:
        PIDFactory.last_unique_id += 1
        return ParagraphId(PIDFactory.last_unique_id)

    def make_invalid_id(self) -> ParagraphId:
        return ParagraphId(-1)


class ParagraphNodes(Dict[ParagraphId, Paragraph]):
    def __setitem__(self, key, value):
        assert key not in self
        return super().__setitem__(key, value)


@dataclass
class Line:
    start: int
    end: int
    row: int
    p_id: ParagraphId


class ParagraphsList(linked_list.LinkedList[ParagraphId, Paragraph]):

    def lines(self, width: int) -> List[Line]:
        def f(p_offsets: Tuple[ParagraphId, List[Tuple[int, int]]], results: List[Line]):
            p_id, lines_start_end = p_offsets
            results.extend(Line(start, end, i, p_id) for i, (start, end) in enumerate(lines_start_end))
            return results

        return func.foldl(
            f=f,
            seq=[(p_id, self[p_id].lines_start_end(width)) for p_id in self.get_ordered_ids()],
            initial=[],
        )

    def merge(self, p_id1: ParagraphId, p_id2: ParagraphId):
        p1 = self[p_id1]
        p2 = self[p_id2]
        p1.text += p2.text
        self.remove(p_id2)


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

    def __repr__(self):
        return f'p_id: {self.p_id}, offset: {self.offset}'


class CalculateCursor:
    text_editor: 'TextEditor'

    def __init__(self, text_editor: 'TextEditor'):
        self.text_editor = text_editor

    @property
    def cursor(self) -> Cursor:
        return self.text_editor.cursor

    @property
    def paragraphs(self) -> ParagraphsList:
        return self.text_editor.paragraphs

    def get_cursor_coord(self, width: int) -> Coord:
        this_p_id = self.cursor.p_id

        def get_line_offsets(_p_id: ParagraphId):
            return TextFormat(self.paragraphs[_p_id].text, width).get_line_offsets()

        # First, add up the number of lines in the previous paragraphs
        num_preceeding_lines = func.foldl(
            f=lambda _p_id, acc: acc + len(get_line_offsets(_p_id)),
            seq=func.take_until(
                pred=lambda _p_id: _p_id == this_p_id,
                seq=self.paragraphs.get_ordered_ids()
            ),
            initial=0,
        )

        # Now calculate the cursor position for this paragraph
        lines_offsets = get_line_offsets(this_p_id)

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

        # Add back in the lines from previous paragraphs
        return Coord(x=x, y=(y + num_preceeding_lines))

    def get_offset_from_coord(self, p_id: ParagraphId, width: int, coord: Coord) -> int:
        line_offsets = TextFormat(self.paragraphs[p_id].text, width).get_line_offsets()
        assert coord.y < len(line_offsets)
        new_offset = line_offsets[coord.y] + coord.x
        return new_offset

    @property
    def paragraph(self) -> Paragraph:
        return self.paragraphs[self.cursor.p_id]

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

    def is_p_origin(self, cursor: Cursor = None):
        if cursor is None:
            cursor = self.cursor

        return cursor.offset == 0

    def is_origin(self):
        return self.cursor.p_id == self.paragraphs.first and self.cursor.offset == 0

    def is_p_end(self, cursor: Cursor = None):
        if cursor is None:
            cursor = self.cursor

        return cursor.offset == self.paragraphs[cursor.p_id].num_chars()
    
    def is_end(self):
        return self.cursor.p_id == self.paragraphs.last and self.cursor.offset == len(self.paragraph.text)

    def get_incr_cursor(self, cursor: Cursor = None) -> Cursor:
        if cursor is None:
            cursor = self.cursor

        if not self.is_p_end(cursor=cursor):
            return cursor.with_offset(cursor.offset + 1)
        elif next_paragraph_id := self.paragraphs.get_next(cursor.p_id):
            return self.get_paragraph_origin(next_paragraph_id)
        else:
            return cursor

    def get_decr_cursor(self, cursor: Cursor = None) -> Cursor:
        if cursor is None:
            cursor = self.cursor

        if not self.is_p_origin():
            return cursor.with_offset(cursor.offset - 1)
        elif prev_p_id := self.paragraphs.get_previous(cursor.p_id):
            return self.get_paragraph_end(prev_p_id)
        else:
            return cursor

    def get_incr_word_cursor(self) -> Cursor:
        # Keep incrementing until the cursor is at a space character, or at a new paragraph, or at the end
        original_p = self.cursor.p_id
        cursor = self.cursor
        while True:
            new_cursor = self.get_incr_cursor(cursor=cursor)
            if self.is_p_end(cursor=new_cursor):
                return new_cursor
            elif self.text_editor.get_character(new_cursor) == ' ':
                return new_cursor
            elif new_cursor.p_id != original_p:
                return new_cursor
            cursor = new_cursor

    def get_decr_word_cursor(self) -> Cursor:
        # Keep decrementing until the cursor is at a space character, or at a new paragraph, or at the beginning
        original_p = self.cursor.p_id
        cursor = self.cursor
        while True:
            new_cursor = self.get_decr_cursor(cursor=cursor)
            if self.is_p_origin(cursor=new_cursor):
                return new_cursor
            elif self.text_editor.get_character(new_cursor) == ' ':
                return new_cursor
            elif new_cursor.p_id != original_p:
                return new_cursor
            cursor = new_cursor

    def __get_corrected_cursor_for_coord(self, width: int, coord: Coord) -> Cursor:
        coord_y = coord.y
        if coord.y < 0:
            return Cursor(self.paragraphs.first, 0)

        lines = self.paragraphs.lines(width)
        if coord.y >= len(lines):
            return Cursor(lines[-1].p_id, len(self.paragraphs[lines[-1].p_id].text))

        line = lines[coord_y]

        new_x = min(coord.x, line.end)
        new_paragraph_y = line.row
        new_offset = self.get_offset_from_coord(line.p_id, width, Coord(x=new_x, y=new_paragraph_y))
        return Cursor(lines[coord_y].p_id, new_offset)

    def get_cursor_for_incr_row(self, width) -> Cursor:
        coord_uncorrected = self.get_cursor_coord(width)
        coord_uncorrected.y += 1
        return self.__get_corrected_cursor_for_coord(width, coord_uncorrected)

    def get_cursor_for_decr_row(self, width) -> Cursor:
        coord_uncorrected = self.get_cursor_coord(width)
        coord_uncorrected.y -= 1
        return self.__get_corrected_cursor_for_coord(width, coord_uncorrected)


class TextEditor:

    paragraphs: ParagraphsList
    cursor: Cursor
    calculate_cursor: CalculateCursor

    def __init__(self, text: str):
        self.reset(text)

    @property
    def active_paragraph(self) -> Paragraph:
        return self.paragraphs[self.cursor.p_id]

    def get_character(self, cursor: Cursor) -> str | None:
        return self.paragraphs[cursor.p_id].get_char(cursor.offset)

    def reset(self, text: str):
        text_parts = text.split('\n')
        if not text_parts:
            # There should be at least one paragraph
            text_parts = ['']
        self.paragraphs = ParagraphsList(Paragraph(p) for p in text_parts)
        self.cursor = Cursor(self.paragraphs.first, 0)
        self.calculate_cursor = CalculateCursor(self)

    def add_character(self, c: str, cursor: Cursor):
        self.paragraphs[cursor.p_id].add_character(c, cursor.offset)

    def remove_character(self, cursor: Cursor):
        paragraph = self.paragraphs[cursor.p_id]
        if cursor.offset < paragraph.num_chars():
            paragraph.remove_character(cursor.offset)

    def split_paragraph(self, cursor: Cursor, new_id: ParagraphId | None = None):
        if new_id is None:
            new_id = self.paragraphs.make_unique_id()
        this_paragraph = self.paragraphs[cursor.p_id]
        text1 = this_paragraph.text[:cursor.offset]
        text2 = this_paragraph.text[cursor.offset:]
        this_paragraph.text = text1
        new_paragraph = Paragraph(text2)
        self.paragraphs.insert_item_after(cursor.p_id, new_paragraph, new_id=new_id)

    def get_data(self):
        return '\n'.join(p.text for p in self.paragraphs.iter_values())
