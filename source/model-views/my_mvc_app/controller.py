class CounterController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.view.button.clicked.connect(self.handle_increment)

    def handle_increment(self):
        self.model.increment()
        new_value = self.model.get_count()
        self.view.update_label(new_value)