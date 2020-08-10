import React, {Component, PureComponent} from "react";
import {
    MDBBtn,
    MDBCol,
    MDBContainer,
    MDBIcon,
    MDBInput,
    MDBNavbarBrand, MDBNavItem, MDBNavLink,
    MDBRow,
    MDBTable,
    MDBTableBody,
    MDBTableHead, MDBTooltip
} from "mdbreact";
import {
  BarChart, Bar, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from 'recharts';
import FormUtils from "../FormUtils";
import axios from "axios";
import * as HttpStatus from "http-status-codes";
import {Redirect} from "react-router-dom";
import PropTypes from "prop-types";
import io from "socket.io-client";




let server_url = "https://localhost:443/"

export class ViewStats extends Component {
    state = {
        start_date: "",
        end_date: "",
        errors: FormUtils.defaultViewStats(),
        been_submitted: false,
        search_result: [],
        msg: "",
        socket: null,
    }


    createRealtimeSocket = () => {
            if (this.state.socket === null || !this.state.socket.connected) {
                this.state.socket = io.connect(server_url + "stats")
                this.state.socket.on("stats", (msg) => {
                    if (!msg['data']){
                        return
                    }
                    else{
                        msg = msg['data']
                    }
                    console.log(msg)
                    console.log(this.state.search_result)
                    let new_arr = this.state.search_result.slice()
                    if (new_arr.length > 0){
                        let last_col = new_arr[new_arr.length-1]
                        if(last_col['date'] === msg['date']){
                            new_arr.pop()
                        }
                    }
                    new_arr.push(msg)
                    this.setState({
                         search_result: new_arr
                    }, this.forceUpdate)

                });
            }
    }

    componentWillUnmount() {
        if (this.state.socket != null){
            this.state.socket.close()
        }
    }

    updateStats = () => {
       let real_data = []
       for(let entry in this.state.search_result)
       {
           let curr = this.state.search_result[entry]
           real_data.push({Date: curr['date'], Guest: curr['Guest'], LoggedIn: curr['Logged in'],
               Manager:curr['Manager'] , Owner: curr['Owner'], SystemManager: curr['System Manager']})
       }
       return real_data
   } ;

  renderResults() {
    return (
      <BarChart
        width={1000}
        height={450}
        data={this.updateStats()}
        margin={{
          top: 20, right: 30, left: 20, bottom: 5,
        }}
      >
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="Date" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="Guest" stackId="a" fill="#84d8bb" />
        <Bar dataKey="LoggedIn" stackId="a" fill="#84add8" />
        <Bar dataKey="Owner" stackId="a" fill="#bd84d8" />
        <Bar dataKey="Manager" stackId="a" fill="#d89c84" />
        <Bar dataKey="SystemManager" stackId="a" fill="#d8849c" />
      </BarChart>
    );
  }

    formUtils = new FormUtils();
    validateStartDate = () =>this.formUtils.validate_start_date(this.state.start_date, this.state.errors);
    validateEndDate = () => this.formUtils.validate_end_date(this.state.end_date, this.state.errors)

    createTodayDate = () => {
        let today = new Date();
        let dd = String(today.getDate()).padStart(2, '0');
        let mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
        let yyyy = today.getFullYear();

        today = dd + '/' + mm + '/' + yyyy;
        return today
    }

    onChange = (e) => {
        this.setState({[e.target.name]: e.target.value});
    };

    clearErrors = () => {
        this.setState({errors: FormUtils.defaultViewStats()})
    }
    sendIfPossible = () => {

        let today = this.createTodayDate()
        if (this.formUtils.compare(this.state.start_date, today) === 0 ||
            this.formUtils.compare(this.state.end_date, today) === 0){
            this.createRealtimeSocket()
        }
        else{
            if(this.state.socket != null){
              this.state.socket.disconnect()
            }
        }
        if (this.state.errors["is_valid"]) {
            axios.get(
                `/system_admin_stats`,
                {
                    params: {
                        start_date: this.state.start_date,
                        end_date: this.state.end_date
                    }
                }
            )

                .then((res) => {
                    // this.props.updateParent.bind(this)(res)
                    this.dealWithSearchResult(res);
                }).catch(error => {
                console.log(error)
                this.dealWithSearchResult(error.response);
            });
        }
    }

    updateSearchResults = (res) => {
        let entry_list = []
        for (let entry in res.data){
            entry_list.push(res.data[entry])
        }
        this.setState({search_result: entry_list})
    }

    dealWithSearchResult = (res) => {
        if (res) {
            if (res.status === HttpStatus.OK) {
                this.updateSearchResults(res);
                if (this.props.getUserId() === -1) {
                    this.props.updateParent(res)
                }
            } else {
                this.setState({msg: this.convertErrorToMessage(res.data["error"])})
            }
        }
    };

    convertErrorToMessage = (msg) => {
        if (msg) {
            msg = msg.split("|").join(", ");
            msg = msg.split("_").join(" ");
            return msg;
        }
    }


    handleNewSearch = () => {
        this.clearErrors();
        let new_errors = this.formUtils.validate_dates(this.state.start_date, this.state.end_date);
        if (new_errors["is_valid"]) {
            this.setState({
                    been_submitted: true,
                    errors: new_errors
                },
                this.sendIfPossible);
        }
    }

    onSubmit = (e) => {
        e.preventDefault();
        this.handleNewSearch();
    }

    render() {
        return (
            <React.Fragment>
                <MDBContainer style={{padding: "10px"}}>
                    <MDBRow
                        style={{
                            display: "flex",
                            alignItems: "left",
                            justifyContent: "left",
                        }}>
                        <MDBCol md="2">
                            <form className="needs-validation" onSubmit={this.onSubmit} noValidate>
                                <p onChange={this.onChange} className="h4 text-center mb-4">View Statistics</p>
                                <div className="grey-text">
                                    <div className="form-group">
                                        <label htmlFor="defaultFormRegisterEmailEx" className="grey-text">
                                            Start Date
                                        </label>
                                        <MDBInput onChange={this.onChange} value={this.state.start_date}
                                                  name="start_date"
                                                  label="dd/mm/yyyy" icon="calendar-day" group type="text"
                                                  id="defaultFormRegisterNameEx"
                                                  className={this.state.been_submitted ? (this.validateStartDate() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                                  required
                                                  error="wrong"
                                                  success="right"/>
                                        <div className="invalid-feedback"
                                             style={{display: "block"}}>{this.state.errors["start_date"]}</div>
                                        <div className="valid-feedback"/>
                                    </div>
                                    <div className="form-group">
                                        <label htmlFor="defaultFormRegisterEmailEx" className="grey-text">
                                            End Date
                                        </label>
                                        <MDBInput onChange={this.onChange} value={this.state.end_date}
                                                  name="end_date"
                                                  label="dd/mm/yyyy" icon="calendar-day" group type="text"
                                                  id="defaultFormRegisterNameEx"
                                                  className={this.state.been_submitted ? (this.validateEndDate() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                                  required
                                                  error="wrong"
                                                  success="right"/>
                                        <div className="invalid-feedback"
                                             style={{display: "block"}}>{this.state.errors["end_date"]}</div>
                                        <div className="valid-feedback"/>
                                    </div>
                                    <div className="text-center">
                                        <MDBBtn type="submit"
                                                value="Submit"
                                                outline
                                                color="info">View</MDBBtn>
                                    </div>
                                </div>
                            </form>
                            <p onChange={this.onChange}
                               className="h3 text-center mb-4 text-danger">{this.state.msg}</p>
                        </MDBCol>
                        <MDBCol md="6">
                            {this.renderResults()}
                        </MDBCol>
                    </MDBRow>

                </MDBContainer>
            </React.Fragment>
        );
    }
}

// PropTypes
ViewStats.propTypes = {
    isLoggedIn: PropTypes.func.isRequired,
    isAdmin: PropTypes.func.isRequired,
    updateParent: PropTypes.func.isRequired,
    getUserId: PropTypes.func.isRequired,
    getUserName: PropTypes.func.isRequired,
};


export default ViewStats;