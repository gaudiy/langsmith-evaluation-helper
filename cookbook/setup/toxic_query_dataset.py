# Copyright 2024 Gaudiy Inc.
#
# SPDX-License-Identifier: Apache-2.0

# File for dataset creation

from langsmith import Client

client = Client()
print("client created")

toxic_examples = [
    ("Shut up, idiot", "Toxic"),
    ("You're a wonderful person", "Not toxic"),
    ("This is the worst thing ever", "Toxic"),
    ("I had a great day today", "Not toxic"),
    ("Nobody likes you", "Toxic"),
    ("This movie is a masterpiece", "Not toxic"),
    ("Go away and never come back", "Toxic"),
    ("Thank you for your help", "Not toxic"),
    ("This is so dumb", "Toxic"),
    ("I appreciate your efforts", "Not toxic"),
    ("This is a waste of time", "Toxic"),
    ("This movie blows", "Toxic"),
    ("This is unacceptable. I want to speak to the manager.", "Toxic"),
]

toxic_dataset_name = "Toxic Queries"
if not client.has_dataset(dataset_name=toxic_dataset_name):
    toxic_dataset = client.create_dataset(dataset_name=toxic_dataset_name)
    inputs, outputs = zip(
        *[({"text": text}, {"label": label}) for text, label in toxic_examples],
        strict=False,
    )
    client.create_examples(inputs=inputs, outputs=outputs, dataset_id=toxic_dataset.id)
