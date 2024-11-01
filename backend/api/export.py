from import_export import fields, resources

from recipes.models import IngredientRecipe


class RecipeExport(resources.ModelResource):
    amount = fields.Field(column_name='amount')
    ingredient__name = fields.Field(column_name='name')
    ingredient__measurement_unit = fields.Field(column_name='measurement_unit')

    class Meta:
        model = IngredientRecipe
        fields = ['amount', 'ingredient__name', 'ingredient__measurement_unit']

    def dehydrate_ingredient_recipe(self, obj):
        if obj is not None:
            return [ingredient for ingredient in obj.amount.all()]
