import matplotlib.pyplot as plt
from matplotlib_venn import venn2_unweighted
# Define 2 sets
A = set("Do you like green eggs and ham?".replace("?", "").lower().split())
B = set("I do not like green eggs and ham".lower().split())
# Create and instance of a venn diagram with 2 areas
diagram = venn2_unweighted([A, B], ("Set A", "Set B"))
# Set text content of areas
diagram.get_label_by_id("10").set_text("\n".join(A - B))
diagram.get_label_by_id("11").set_text("\n".join(A & B))
diagram.get_label_by_id("01").set_text("\n".join(B - A))
# Modify font sizes
for text in diagram.set_labels:
 text.set_fontsize(24)
for text in diagram.subset_labels:
 text.set_fontsize(20)
plt.gcf().canvas.set_window_title('Fun With Venn Diagrams')  # Set window title
plt.show()