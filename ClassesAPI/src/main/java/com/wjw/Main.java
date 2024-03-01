package com.wjw;

import com.google.cloud.functions.HttpFunction;
import com.google.cloud.functions.HttpRequest;
import com.google.cloud.functions.HttpResponse;
import com.google.firebase.cloud.FirestoreClient;
import com.squareup.moshi.Moshi;
import com.squareup.moshi.Types;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutionException;

public class Main implements HttpFunction {
    @Override
    public void service(HttpRequest httpRequest, HttpResponse httpResponse) throws IOException, ExecutionException, InterruptedException {
        // load the singleton that stores the Firebase configuration to ensure it's created
        Infrastructure.getInstance();

        // get the collection of course documents for the given term
        var db = FirestoreClient.getFirestore();
        var qry = db.collection("202108")
                .orderBy("dept")
                .orderBy("course_nbr")
                .get();
        var documents = qry.get().getDocuments();

        // convert to POJO and add to list
        ArrayList<Course> courseList = new ArrayList<Course>();
        for (var document :
                documents) {
            var course = document.toObject(Course.class);
            courseList.add(course);
        }

        // deserialize the list to JSON
        var moshi = new Moshi.Builder().build();
        var jsonAdapter = moshi.adapter(Types.newParameterizedType(List.class,Course.class));

        String json = jsonAdapter.toJson(courseList);

        // write the response
        var writer = httpResponse.getWriter();
        writer.write(json);
    }
}
