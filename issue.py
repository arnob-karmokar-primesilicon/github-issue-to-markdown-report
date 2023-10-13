class Issue:
    def __init__(self, title, url, is_closed, created_at, closed_at, project_title, project_status, start_date, complete_date, deadline):
        self.title = title
        self.url = url
        self.is_closed = is_closed
        self.created_at = created_at
        self.closed_at = closed_at
        self.project_title = project_title
        self.project_status = project_status
        self.start_date = start_date
        self.complete_date = complete_date
        self.deadline = deadline

    def __str__(self):
        return f"Issue Title: {self.title}\nURL: {self.url}\nIs Closed: {self.is_closed}\nCreated At: {self.created_at}\nClosed At: {self.closed_at}\nProject Title: {self.project_title}\nProject Status: {self.project_status}\nStart Date: {self.start_date}\nComplete Date: {self.complete_date}\nDeadline: {self.deadline}\n"