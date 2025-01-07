from pydantic import BaseModel


class FolderStat(BaseModel):
    folder_title: str
    peers_len: int

    def to_text(self) -> str:
        return f'{self.folder_title} - {self.peers_len}'


class FoldersCategoryStat(BaseModel):
    folders_stat: list[FolderStat]

    @property
    def total_count(self) -> int:
        return sum(folder_stat.peers_len for folder_stat in self.folders_stat)

    def to_text(self) -> str:
        stat = '\n'.join(folder_stat.to_text() for folder_stat in self.folders_stat)
        # stat += f'\n\nВсего: {self.total_count}'

        return stat