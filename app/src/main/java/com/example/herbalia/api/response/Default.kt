package com.example.herbalia.api.response

import com.google.gson.annotations.SerializedName

data class Default(
    @SerializedName("nama")
    var nama:String?,
    @SerializedName("deskripsi")
    var deskripsi:String?,
    @SerializedName("khasiat")
    var khasiat:String?,
    @SerializedName("Message")
    var message:String?
)

