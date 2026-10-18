for idx, row in df.iterrows():

    article_text = f"""
    Company: {row['company_name']}
    Date: {row['Date']}

    Article:
    {row['Document']}

    Source:
    {row['URL']}
    """
    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=article_text
    ).data[0].embedding

    collection.add(
        ids=[str(idx)],
        embeddings=[embedding],
        documents=[article_text],
        metadatas=[{
            "company": row["company_name"],
            "date": str(row["Date"]),
            "url": row["URL"]
            
        }]
    )
