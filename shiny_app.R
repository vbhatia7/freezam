#########################################
### Author: Vinni Bhatia
### Last Edited: Dec 17, 2020
### Use: Combines R and Python to build a Shiny App
#########################################

library(shiny)
library(shinythemes)
library(reticulate)
library(shinyFiles)
library(sjmisc)
library(geniusr)
library(stringr)



#py_run_file("database_manager.py")
source_python("database_manager.py")
source_python("spectral_analysis.py")
source_python("audio_processing.py")



# Define UI for data upload app ----
ui <- fluidPage(theme = shinytheme("sandstone"),
  
  # App title ----
  titlePanel(h1("Finding Music Matches"
                )),
  
  # Sidebar layout with input and output definitions ----
  sidebarLayout(
    
    # Sidebar panel for inputs ----
    sidebarPanel(
      
      shinyFilesButton('file1', label='Choose a WAV snippet',
                       title='Please select a file', multiple=FALSE),
                       #filename = "C:/snippets/jarofhearts_snippet.wav",
                       #filetype = "wav"),
      textOutput("txt_file"),
      
      br(),

      textInput("url", "Upload a .wav or .mp3 from a URL", value = "", width = NULL,
                placeholder = NULL),
      textOutput("value"),
      # 
      actionButton("recording", "Record audio", icon = NULL, width = "200px"),
      hr(style = "border-top: 1px dotted #000000;"),
      
      shinyDirButton('folder1', label='Get Recommendations (Folder)',
                       title='Please select a folder'),
      textOutput("txt_folder"),
      br(),
      # Horizontal line ----
      hr(style = "border-top: 2px solid #000000;"),
      #tags$hr(style="border-color: purple;"),
      
      
      # Input: Select Method ----
      radioButtons("method", "Method",
                   choices = c(`Frequencies where Max Peaks occur`= "one",
                               `Max Peaks in Eight Increasing Octaves` = "five"),
                   selected = "one"),
      
      # Input: Select Epsilon ----
      numericInput("epsilon", "Epsilon (distance-threshold):", 1e-06),
                   
      
      # Horizontal line ----
      #tags$hr(style="border-color: purple;")
      
    ),
    
    # Main panel for displaying outputs ----
    mainPanel(
      
      # Output: Data file ----
      htmlOutput("step1"),
      htmlOutput("text_intro"),
      htmlOutput("step2"),
      #textInput("notice", "Recording Status", "Nothing recorded."),
      textOutput("time_remaining"),
      htmlOutput("text_spec"),
      imageOutput("plot1"),
      br(),
      br(),
      htmlOutput("step3"),
      htmlOutput("text_audio"),
      verbatimTextOutput("text_results"),
      htmlOutput("great"),
      htmlOutput("lyrics")
    )
    
  )
)


# Define server logic to read selected file ----
server <- function(input, output, session) {

  output$step1 <- renderUI({
    HTML("<header> 
           <h2><b>Step 1<b></h1> 
           </header>")
  })
  output$text_intro <- renderUI({ 
    HTML("Welcome to Freezam! <br/> <br/>
        To begin, please use the left-hand panel to either upload a snippet of 
         a song you would like to be matched too, a URL to a WAV or MP3 snippet,
         or select the 'record' option. The record option will record 25 seconds of audio. 
         Alternatively, you can also choose to get some recommendations to artists and songs by instead selecting a folder with songs inside! <br/> <br/>
         Also, please be sure to select your preferred method of fingerprinting, and specified epsilon value. <br/> <br/>")
  })
  
  volumes = getVolumes()
  shinyFileChoose(input, "file1", roots = volumes, session = session)
  observeEvent(input$file1,{  
    req(input$file1)
    results = ""
    if(!is.null(input$file1)){
      file_selected<-parseFilePaths(volumes, input$file1)
      output$txt_file <- renderText(as.character(file_selected$datapath))
      
      output$plot1 <- renderImage({
        plot_spectrogram_file(as.character(file_selected$datapath))
        list(src = "C:/Users/vinay/Documents/s750/assignments-vbhatia7/shazam/temp/temp_plot.png")
      }, deleteFile = FALSE)
      output$step2 <- renderUI({
        HTML("<header> 
           <h2><b>Step 2<b></h1> 
           </header>")
      })
      output$text_spec <- renderUI({ 
        HTML("You have chosen to use a local snippet. <br/> <br/>
        Let's display the spectrogram first. (For more info on what a spectrogram is,
             please visit: <a href=https://en.wikipedia.org/wiki/Spectrogram>the Wikipedia article</a>.)")
      })
      output$step3 <- renderUI({
        HTML("<header> 
           <h2><b>Step 3<b></h1> 
           </header>")
      })
      output$text_audio <- renderUI({ 
        HTML("Now let's check to see if it matches to anything in our database. <br/> <br/>
        Calculating... <br/> <br/>")
      })
      output$text_results <- renderPrint({
        results = fast_search(path = as.character(file_selected$datapath),
                              source = "local",
                              epsilon = input$epsilon,
                              method = input$method)
        
        print(results)
        song_name = str_trim(sub("by.*","",sub('.*:', '', results)))
        artist_name = str_trim(sub(".*by","",sub('.*:', '', results)))
        df_lyrics = try(get_lyrics_search(artist_name = artist_name,
                                      song_title = song_name), silent = T)
        if(str_contains(results, "could not find")){
          output$great <- renderUI({
            HTML("<br/> <br/> Unfortunately, it doesn't look like Freezam was able to find a close match. Perhaps try a longer snippet. <br/> <br/>")
          })
          output$lyrics <- renderUI({
            HTML(" ")
          })
        }
        if(str_contains(results, "Match Found!")){
          output$great <- renderUI({
            HTML("<br/> It looks like Freezam was able to find a match! <br/>
            Maybe you'd like to see the lyrics - let me try to fetch those for you by scraping <a href=https://genius.com>Genius</a>. <br/> <br/>")
          })
          if (class(df_lyrics) != "try-error"){
            output$lyrics <- renderUI({
              HTML(paste("<header><h2><b>Lyrics<b></h1></header>",
                         paste(df_lyrics$line, collapse = "<br/>"),  collapse = "<br/>"))
            })
          }
          else{
            output$lyrics <- renderUI({
              HTML("Unfortunately, the lyrics do not appear to be easily scrapable. <br/> <br/>")
            })
          }
        }
      })
    }
  })
  
  shinyDirChoose(input, "folder1", roots = volumes(), session = session)
  observeEvent(input$folder1,{
    req(input$folder1)
    results = ""
    if(!is.null(input$folder1)){
      folder_selected<-parseDirPath(volumes, input$folder1)
      print(folder_selected)
      #print(folder_selected$datapath)
      output$txt_folder <- renderText(as.character(folder_selected))

      output$step2 <- renderUI({
        HTML("<header>
           <h2><b>Step 2<b></h1>
           </header>")
      })

      output$text_spec <- renderUI({
        HTML("You have chosen to recommend some songs! <br/> <br/>
             Please wait while the system finds some matches. <br/> <br/>
             Calculating... <br/> <br/>")
      })
      output$step3 <- renderUI({
        HTML("<header>
           <h2><b>Step 3<b></h1>
           </header>")
      })
      output$great <- renderUI({
        results = recommend(as.character(folder_selected))
        #print(results)
        #print(paste(names(results[[1]]), collapse = "<br/>"))
        HTML(paste("<header><h3>10 Closest Songs</h3></header>",
                     paste(names(results[[1]]), collapse = "<br/>"),
                   "<header><h3>10 Closest Artists</h3></header>",
                   paste(names(results[[2]]), collapse = "<br/>"),
                   collapse = "<br/>"))
        #print(results)
      })
    }
  })
  

  observeEvent( input$url, {
    req(input$url)
    if(!is.null(input$url)) {
      convert_to_local_wav(as.character(input$url), source = "url")
      output$value <- renderText(paste(as.character(input$url)))
      output$plot1 <- renderImage({
        plot_spectrogram_file(paste0("WAVs/", basename(as.character(input$url))))
        list(src = "C:/Users/vinay/Documents/s750/assignments-vbhatia7/shazam/temp/temp_plot.png")
      }, deleteFile = FALSE) 
      output$step2 <- renderUI({
        HTML("<header> 
           <h2><b>Step 2<b></h1> 
           </header>")
      })
      output$text_spec <- renderUI({ 
        HTML("You have chosen to upload a file. <br/> <br/>
        Let's display the spectrogram first. (For more info on what a spectrogram is,
             please visit: <a href=https://en.wikipedia.org/wiki/Spectrogram>the Wikipedia article</a>.)")
      })
      output$step3 <- renderUI({
        HTML("<header> 
           <h2><b>Step 3<b></h1> 
           </header>")
      })
      output$text_audio <- renderUI({ 
        HTML("This audio file is now in our database. <br/> <br/>
        Let's check to see if it matches to anything in there. <br/> <br/>
        Calculating... <br/> <br/>")
      })
      output$text_results <- renderPrint({
        results = fast_search(path = paste0("WAVs/", basename(as.character(input$url))),
                              source = "local",
                              epsilon = input$epsilon,
                              method = input$method)
        
        print(results)
        song_name = str_trim(sub("by.*","",sub('.*:', '', results)))
        artist_name = str_trim(sub(".*by","",sub('.*:', '', results)))
        df_lyrics = try(get_lyrics_search(artist_name = artist_name,
                                          song_title = song_name), silent = T)
        if(str_contains(results, "could not find")){
          output$great <- renderUI({
            HTML("<br/> <br/> Unfortunately, it doesn't look like Freezam was able to find a close match. Perhaps try a longer snippet. <br/> <br/>")
          })
          output$lyrics <- renderUI({
            HTML(" ")
            rm(df_lyrics)
          })
        }
        if(str_contains(results, "Match Found!")){
          output$great <- renderUI({
            HTML("<br/> It looks like Freezam was able to find a match! <br/>
            Maybe you'd like to see the lyrics - let me try to fetch those for you by scraping <a href=https://genius.com>Genius</a>. <br/> <br/>")
          })
          if (class(df_lyrics) != "try-error"){
            output$lyrics <- renderUI({
              HTML(paste("<header><h2><b>Lyrics<b></h1></header>",
                         paste(df_lyrics$line, collapse = "<br/>"),  collapse = "<br/>"))
            })
          }
          else{
            output$lyrics <- renderUI({
              HTML("Unfortunately, the lyrics do not appear to be easily scrapable. <br/> <br/>")
            })
          }
        }
      })
    }
  })
  
  observeEvent( input$recording, {
    req(input$recording)
    if(!is.null(input$recording)) {
      output$step2 <- renderUI({
        HTML("<header> 
           <h2><b>Step 2<b></h1> 
           </header>")
      })
      
      record_song()

      output$plot1 <- renderImage({
        plot_spectrogram_file("temp/output.wav")
        list(src = "C:/Users/vinay/Documents/s750/assignments-vbhatia7/shazam/temp/temp_plot.png")
      }, deleteFile = FALSE)
      output$text_spec <- renderUI({
        HTML("You have chosen to record some audio. <br/> <br/>
        Let's display the spectrogram first. (For more info on what a spectrogram is,
             please visit: <a href=https://en.wikipedia.org/wiki/Spectrogram>the Wikipedia article</a>.)")
      })
      output$step3 <- renderUI({
        HTML("<header>
           <h2><b>Step 3<b></h1>
           </header>")
      })
      output$text_audio <- renderUI({
        HTML("Now let's check to see if this recorded audio matches to anything in our database. <br/> <br/>
        Calculating... <br/> <br/>")
      })
      output$text_results <- renderText({
        results = fast_search(path = "temp/output.wav",
                              source = "local",
                              epsilon = input$epsilon,
                              method = input$method)
        
        print(results)
        song_name = str_trim(sub("by.*","",sub('.*:', '', results)))
        artist_name = str_trim(sub(".*by","",sub('.*:', '', results)))
        df_lyrics = try(get_lyrics_search(artist_name = artist_name,
                                          song_title = song_name), silent = T)
        if(str_contains(results, "could not find")){
          output$great <- renderUI({
            HTML("<br/> <br/> Unfortunately, it doesn't look like Freezam was able to find a close match. Perhaps try a longer snippet. <br/> <br/>")
          })
          output$lyrics <- renderUI({
            HTML(" ")
            rm(df_lyrics)
          })
        }
        if(str_contains(results, "Match Found!")){
          output$great <- renderUI({
            HTML("<br/> It looks like Freezam was able to find a match! <br/>
            Maybe you'd like to see the lyrics - let me try to fetch those for you by scraping <a href=https://genius.com>Genius</a>. <br/> <br/>")
          })
          if (class(df_lyrics) != "try-error"){
            output$lyrics <- renderUI({
              HTML(paste("<header><h2><b>Lyrics<b></h1></header>",
                         paste(df_lyrics$line, collapse = "<br/>"),  collapse = "<br/>"))
            })
          }
          else{
            output$lyrics <- renderUI({
              HTML("Unfortunately, the lyrics do not appear to be easily scrapable. <br/> <br/>")
            })
          }
        }
      })
    }
  })

}
# Run the app ----
shinyApp(ui, server)




