import React, {Component} from "react";
import {MDBBtn, MDBCol, MDBContainer, MDBInput, MDBRow} from 'mdbreact';
import PropTypes from "prop-types";
import FormUtils from "../FormUtils";
import axios from "axios";
import * as HttpStatus from "http-status-codes"
import {Redirect} from "react-router-dom";

class PurchaseItemsPage extends Component {
    state = {
        credit_card: "",
        country: "",
        city: "",
        street: "",
        house_number: "",
        apartment: "",
        floor: "",
        expiry_date: "",
        ccv:"",
        holder:"",
        holder_id:"",
        errors: FormUtils.defaultPurchaseItemsDictionary(),
        been_submitted: false,
        msg: "",
        redirectAfterRegistered: null
    };
    formUtils = new FormUtils();


    validateCreditCard = () => this.formUtils.validate_credit_card(this.state.credit_card, this.state.errors);

    validateCountry = () => this.formUtils.validate_country(this.state.country, this.state.errors);
    validateCity = () => this.formUtils.validate_city(this.state.city, this.state.errors);
    validateStreet = () => this.formUtils.validate_street(this.state.street, this.state.errors);
    validateHouseNumber = () => this.formUtils.validate_house_number(this.state.house_number, this.state.errors);
    validateApartment = () => this.formUtils.validate_apartment(this.state.apartment, this.state.errors);
    validateFloor = () => this.formUtils.validate_floor(this.state.floor, this.state.errors);
    validateCCV = () => this.formUtils.validate_ccv(this.state.ccv, this.state.errors);
    validateExpiryDate = () => this.formUtils.validate_expiry_date(this.state.expiry_date, this.state.errors);

    onChange = (e) => {
        this.setState({[e.target.name]: e.target.value});
    };
    clearErrors = () => {
        this.setState({errors: FormUtils.defaultPurchaseItemsDictionary()})
    };
    sendIfPossible = () => {
        if (this.state.errors["is_valid"]) {
            axios.post(
                "/purchase_items",
                {
                    user_id: this.props.getUserId(),
                    credit_card: this.state.credit_card,
                    country: this.state.country,
                    city: this.state.city,
                    street: this.state.street,
                    house_number: this.state.house_number,
                    apartment: this.state.apartment,
                    floor: this.state.floor,
                    expiry_date: this.state.expiry_date,
                    ccv: this.state.ccv,
                    holder: this.state.holder,
                    holder_id: this.state.holder_id
                },
            )
                .then((res) => {
                    console.log(res);
                    this.dealWithRegisterResult(res);
                }).catch(error => {
                console.log(error);
                this.dealWithRegisterResult(error.response);
            });
        }
    };

    dealWithRegisterResult = (res) => {
        if (res) {
            if (res.status === HttpStatus.CREATED || res.status === HttpStatus.OK) {
                // register successful
                this.setState({redirectAfterRegistered: "/watch_shopping_cart"})
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
    };

    onSubmit = (e) => {
        e.preventDefault();
        this.clearErrors();
        let new_errors = this.formUtils.validate_purchase_items(this.state.credit_card, this.state.country, this.state.city, this.state.street, this.state.house_number, this.state.apartment,
            this.state.floor, this.state.ccv, this.state.holder, this.state.holder_id, this.state.expiry_date);
        this.setState({
                been_submitted: true,
                errors: new_errors
            },
            this.sendIfPossible);

    };


    render() {
        if (this.state.redirectAfterRegistered) {
            return <Redirect to={this.state.redirectAfterRegistered}/>
        } else {
            return (
                <React.Fragment>
                    <MDBContainer style={{padding: "10px"}}>
                        <MDBRow
                            style={{
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "center",
                            }}>
                            <MDBCol md="6">

                                <form className="needs-validation" onSubmit={this.onSubmit} noValidate>
                                    <p onChange={this.onChange} className="h3 text-center mb-4">Purchase Items From
                                        Shopping Cart</p>
                                    <p>fill payment and shipping info</p>
                                    <div className="grey-text">
                                        <div className="form-group">
                                            <MDBInput onChange={this.onChange} value={this.state.country}
                                                      name="country"
                                                      label="Country" icon="globe" group type="text"
                                                      id="defaultFormRegisterNameEx"
                                                      className={this.state.been_submitted ? (this.validateCountry() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                                      required
                                                      error="wrong"
                                                      success="right"/>
                                            <div className="invalid-feedback"
                                                 style={{display: "block"}}>{this.state.errors["country"]}</div>
                                            <div className="valid-feedback"/>
                                        </div>
                                    </div>
                                    <div className="grey-text">
                                        <div className="form-group">
                                            <MDBInput onChange={this.onChange} value={this.state.city}
                                                      name="city"
                                                      label="City" icon="city" group type="text"
                                                      id="defaultFormRegisterNameEx"
                                                      className={this.state.been_submitted ? (this.validateCity() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                                      required
                                                      error="wrong"
                                                      success="right"/>
                                            <div className="invalid-feedback"
                                                 style={{display: "block"}}>{this.state.errors["city"]}</div>
                                            <div className="valid-feedback"/>
                                        </div>
                                    </div>
                                    <div className="grey-text">
                                        <div className="form-group">
                                            <MDBInput onChange={this.onChange} value={this.state.street}
                                                      name="street"
                                                      label="Street" icon="road" group type="text"
                                                      id="defaultFormRegisterNameEx"
                                                      className={this.state.been_submitted ? (this.validateStreet() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                                      required
                                                      error="wrong"
                                                      success="right"/>
                                            <div className="invalid-feedback"
                                                 style={{display: "block"}}>{this.state.errors["street"]}</div>
                                            <div className="valid-feedback"/>
                                        </div>
                                    </div>
                                    <div className="grey-text">
                                        <div className="form-group">
                                            <MDBInput onChange={this.onChange} value={this.state.house_number}
                                                      name="house_number"
                                                      label="House Number" icon="home" group type="text"
                                                      id="defaultFormRegisterNameEx"
                                                      className={this.state.been_submitted ? (this.validateHouseNumber() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                                      required
                                                      error="wrong"
                                                      success="right"/>
                                            <div className="invalid-feedback"
                                                 style={{display: "block"}}>{this.state.errors["house_number"]}</div>
                                            <div className="valid-feedback"/>
                                        </div>
                                    </div>
                                    <div className="grey-text">
                                        <div className="form-group">
                                            <MDBInput onChange={this.onChange} value={this.state.apartment}
                                                      name="apartment"
                                                      label="Apartment Identifier (optional)" icon="building" group
                                                      type="text"
                                                      id="defaultFormRegisterNameEx"
                                                      className={this.state.been_submitted ? (this.validateApartment() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                                      required
                                                      error="wrong"
                                                      success="right"/>
                                            <div className="invalid-feedback"
                                                 style={{display: "block"}}>{this.state.errors["apartment"]}</div>
                                            <div className="valid-feedback"/>
                                        </div>
                                    </div>
                                    <div className="grey-text">
                                        <div className="form-group">
                                            <MDBInput onChange={this.onChange} value={this.state.floor}
                                                      name="floor"
                                                      label="Floor (optional)" icon="building" group
                                                      type="text"
                                                      id="defaultFormRegisterNameEx"
                                                      className={this.state.been_submitted ? (this.validateFloor() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                                      required
                                                      error="wrong"
                                                      success="right"/>
                                            <div className="invalid-feedback"
                                                 style={{display: "block"}}>{this.state.errors["floor"]}</div>
                                            <div className="valid-feedback"/>
                                        </div>
                                    </div>
                                    <div className="grey-text">
                                        <div className="form-group">
                                            <MDBInput onChange={this.onChange} value={this.state.credit_card}
                                                      name="credit_card"
                                                      label="Your Credit Card" icon="credit-card" group type="text"
                                                      id="defaultFormRegisterNameEx"
                                                      className={this.state.been_submitted ? (this.validateCreditCard() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                                      required
                                                      error="wrong"
                                                      success="right"/>
                                            <div className="invalid-feedback"
                                                 style={{display: "block"}}>{this.state.errors["credit_card"]}</div>
                                            <div className="valid-feedback"/>
                                        </div>
                                    </div>
                                    <div className="grey-text">
                                        <div className="form-group">
                                            <MDBInput onChange={this.onChange} value={this.state.ccv}
                                                      name="ccv"
                                                      label="CCV" icon="info" group
                                                      type="text"
                                                      id="defaultFormRegisterNameEx"
                                                      className={this.state.been_submitted ? (this.validateCCV() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                                      required
                                                      error="wrong"
                                                      success="right"/>
                                            <div className="invalid-feedback"
                                                 style={{display: "block"}}>{this.state.errors["ccv"]}</div>
                                            <div className="valid-feedback"/>
                                        </div>
                                    </div>
                                    <div className="grey-text">
                                        <div className="form-group">
                                            <MDBInput onChange={this.onChange} value={this.state.expiry_date}
                                                      name="expiry_date"
                                                      label="MM/YY" icon="calendar-check" group type="text"
                                                      id="defaultFormRegisterNameEx"
                                                      className={this.state.been_submitted ? (this.validateExpiryDate() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                                      required
                                                      error="wrong"
                                                      success="right"/>
                                            <div className="invalid-feedback"
                                                 style={{display: "block"}}>{this.state.errors["expiry_date"]}</div>
                                            <div className="valid-feedback"/>
                                        </div>
                                    </div>
                                    <div className="grey-text">
                                        <div className="form-group">
                                            <MDBInput onChange={this.onChange} value={this.state.holder}
                                                      name="holder"
                                                      label="Holder" icon="user" group
                                                      type="text"
                                                      id="defaultFormRegisterNameEx"
                                                      // className={this.state.been_submitted ? (this.validateCCV() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                                      required
                                                      error="wrong"
                                                      success="right"/>
                                            <div className="invalid-feedback"
                                                 style={{display: "block"}}>{this.state.errors["holder"]}</div>
                                            <div className="valid-feedback"/>
                                        </div>
                                    </div>
                                    <div className="grey-text">
                                        <div className="form-group">
                                            <MDBInput onChange={this.onChange} value={this.state.holder_id}
                                                      name="holder_id"
                                                      label="Holder_id" icon="id-card" group
                                                      type="text"
                                                      id="defaultFormRegisterNameEx"
                                                      // className={this.state.been_submitted ? (this.validateCCV() ? "form-control is-valid" : "form-control is-invalid") : 'form-control'}
                                                      required
                                                      error="wrong"
                                                      success="right"/>
                                            <div className="invalid-feedback"
                                                 style={{display: "block"}}>{this.state.errors["holder_id"]}</div>
                                            <div className="valid-feedback"/>
                                        </div>
                                    </div>

                                    <div className="text-center">
                                        <MDBBtn type="submit"
                                                value="Submit"
                                                outline
                                                color="info">Pay</MDBBtn>
                                    </div>
                                </form>
                                <p onChange={this.onChange}
                                   className="h3 text-center mb-4 text-danger">{this.state.msg}</p>
                            </MDBCol>
                        </MDBRow>
                    </MDBContainer>
                </React.Fragment>
            );
        }
    }
}

// PropTypes
PurchaseItemsPage.propTypes = {
    isLoggedIn: PropTypes.func.isRequired,
    isAdmin: PropTypes.func.isRequired,
    updateParent: PropTypes.func.isRequired,
    getUserName: PropTypes.func.isRequired,
};

export default PurchaseItemsPage;

