package com.example.herbalia

import android.app.ProgressDialog
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.util.Log
import android.widget.Toast
import com.bumptech.glide.Glide
import com.example.herbalia.api.ApiConfig
import com.example.herbalia.api.response.Default
import kotlinx.android.synthetic.main.activity_hasil.*
import okhttp3.MediaType
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Call
import retrofit2.Response
import java.io.File

class hasilActivity : AppCompatActivity() {
    lateinit var image: MultipartBody.Part

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_hasil)
        val actionbar = supportActionBar
        actionbar!!.title = "Hasil Scan"
        actionbar.setDisplayHomeAsUpEnabled(true)
        actionbar.setDisplayHomeAsUpEnabled(true)

        // mempilkan image yang akan diupload dengan glide ke imgUpload.
        Glide.with(this).load(intent.getStringExtra("IMG")).into(imgResult)

        val requestBody = RequestBody.create(MediaType.parse("multipart"), File(intent.getStringExtra("IMG")))

        // mengoper value dari requestbody sekaligus membuat form data untuk upload. dan juga mengambil nama dari picked image
        image = MultipartBody.Part.createFormData("image", File(intent.getStringExtra("IMG"))?.name,requestBody)

        Result()

//        btn_Next.setOnClickListener {
//
//        }

    }

    override fun onSupportNavigateUp(): Boolean {
        onBackPressed()
        return true
    }

    private fun Result(){

        // meampilkan progress dialog
        val loading = ProgressDialog(this)
        loading.show()
        loading.setMessage("Mohon Tunggu ... .")

        // init retrofit
        val call = ApiConfig().instance().upload(image)

        // membaut request ke api
        call.enqueue(object : retrofit2.Callback<Default>{

            // handling request saat fail
            override fun onFailure(call: Call<Default>?, t: Throwable?) {
                loading.dismiss()
                Toast.makeText(applicationContext,"Connection error", Toast.LENGTH_SHORT).show()
                Log.d("ONFAILURE",t.toString())
            }

            // handling request saat response.
            override fun onResponse(call: Call<Default>?, response: Response<Default>?) {

                // dismiss progress dialog
                loading.dismiss()

                // menampilkan pesan yang diambil dari response.
                //Toast.makeText(applicationContext,response?.body()?.nm_brg,Toast.LENGTH_SHORT).show()


                TV_nama.setText(response?.body()?.nama)
                TV_deskripsi.setText(response?.body()?.deskripsi)
                TV_khasiat.setText(response?.body()?.khasiat)
                if (response?.body()?.nama.isNullOrBlank()){
                    TV_nama.setText("\"belum terdeteksi silahkan coba lagi\"")
                    TV_khasiat.setText("tidak ada")
                }
            }


        })


    }
}