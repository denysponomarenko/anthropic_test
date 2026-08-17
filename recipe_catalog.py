class RecipeCatalog:
    def __init__(self):
        self.recipes = {}
        self.ratings = {}

    def add_recipe(self, name, ingredients, time):
        if name in self.recipes:
            return False
        self.recipes[name] = (set(ingredients), time)
        self.ratings[name] = []
        return True

    def get_recipe(self, name):
        if name not in self.recipes:
            return None
        ingredients, time = self.recipes[name]
        return (list(ingredients), time)

    def delete_recipe(self, name):
        if name not in self.recipes:
            return False
        del self.recipes[name]
        del self.ratings[name]
        return True

    def search_by_ingredient(self, ingredient):
        return sorted(
            name for name, (ingredients, _) in self.recipes.items()
            if ingredient in ingredients
        )

    def search_by_time(self, max_time):
        return sorted(
            name for name, (_, time) in self.recipes.items()
            if time <= max_time
        )

    def add_rating(self, name, rating):
        if name not in self.recipes or rating < 1 or rating > 5:
            return False
        self.ratings[name].append(rating)
        return True

    def get_top_rated(self, n):
        def avg(name):
            r = self.ratings[name]
            return sum(r) / len(r) if r else 0

        return sorted(
            self.recipes,
            key=lambda name: (-avg(name), name)
        )[:n]

    def suggest_meal(self, available):
        available = set(available)
        possible = []

        for name, (ingredients, _) in self.recipes.items():
            if ingredients <= available:
                possible.append((len(available - ingredients), name))

        return min(possible)[1] if possible else None
